import datetime
import hashlib
import itertools

import stem.util
from stem.descriptor.hidden_service import HiddenServiceDescriptorV3, InnerLayer
from stem.descriptor.certificate import Ed25519CertificateV1, Ed25519Extension, ExtensionType

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from onionbalance.common import log
from onionbalance.common import intro_point_set

from onionbalance.hs_v3 import params

logger = log.get_logger()
backend = default_backend()


class IntroductionPointSetV3(intro_point_set.IntroductionPointSet):
    """
    This class represents a set of introduction points (which are actually
    stem.descriptor.hidden_service.IntroductionPointV3 objects)

    It gives us a nice way to compare sets of introduction poinst between them,
    to see if they are different.

    It also preserves all the functionality of
    onionbalance.common.intro_point_set.IntroductionPointSet which allows you to
    sample introduction points out of the set.
    """

    def __init__(self, introduction_points):
        """
        'introduction_points' is a list of lists where each internal list contains
        the introduction points of an instance
        """
        for instance_ips in introduction_points:
            for ip in instance_ips:
                if ip.legacy_key_raw:
                    logger.info("Ignoring introduction point with legacy key.")
                    instance_ips.remove(ip)

        super().__init__(introduction_points)

    def get_intro_points_flat(self):
        """
        Flatten the .intro_points list of list into a single list and return it
        """
        return list(itertools.chain(*self.intro_points))

    def __eq__(self, other):
        """
        Compares two IntroductionPointSetV3 objects and returns True
        if they have the same introduction points in them.
        """
        # XXX we are currently using onion_key_raw as the identifier for the
        # intro point. is there a better thing to use?
        intro_set_1 = set(ip.onion_key_raw for ip in other.get_intro_points_flat())
        intro_set_2 = set(ip.onion_key_raw for ip in self.get_intro_points_flat())

        # TODO: unittests
        return intro_set_1 == intro_set_2


class V3Descriptor(object):
    """
    A generic v3 descriptor.

    Serves as the base class for OBDescriptor and ReceivedDescriptor which
    implement more specific functionalities.
    """

    def __init__(self, onion_address, v3_desc):
        self.onion_address = onion_address

        self.v3_desc = v3_desc

        # An IntroductionPointSetV3 object with the intros of this descriptor
        self.intro_set = IntroductionPointSetV3([self.v3_desc._inner_layer.introduction_points])

    def get_intro_points(self):
        """
        Get the raw intro points for this descriptor.
        """
        return self.intro_set.get_intro_points_flat()

    def get_blinded_key(self):
        """
        Extract and return the blinded key from the descriptor
        """

        # The descriptor signing cert, signs the descriptor signing key using
        # the blinded key. So the signing key should be the one we want here.
        return self.v3_desc.signing_cert.signing_key()

    def get_size(self):
        """
        Return size of v3 descriptor in bytes
        """
        return len(str(self.v3_desc))


class OBDescriptor(V3Descriptor):
    """
    A v3 descriptor created by Onionbalance and meant to be published to the
    network.

    This class supports generating descriptors.

    Can raise BadDescriptor if we can't or should not generate a valid descriptor.
    """

    def __init__(self, onion_address, identity_priv_key,
                 blinding_param, intro_points, is_first_desc):
        # Timestamp of the last attempt to assemble this descriptor
        self.last_publish_attempt_ts = None
        # Timestamp we last uploaded this descriptor
        self.last_upload_ts = None
        # Set of responsible HSDirs for last time we uploaded this descriptor
        self.responsible_hsdirs = None

        # Start generating descriptor
        desc_signing_key = Ed25519PrivateKey.generate()

        # Get the intro points for this descriptor and recertify them!
        recertified_intro_points = []
        for ip in intro_points:
            recertified_intro_points.append(self._recertify_intro_point(ip, desc_signing_key))

        rev_counter = self._get_revision_counter(identity_priv_key, is_first_desc)

        v3_desc_inner_layer = InnerLayer.create(introduction_points=recertified_intro_points)
        v3_desc = HiddenServiceDescriptorV3.create(
            blinding_nonce=blinding_param,
            identity_key=identity_priv_key,
            signing_key=desc_signing_key,
            inner_layer=v3_desc_inner_layer,
            revision_counter=int(rev_counter),
        )

        # TODO stem should probably initialize it itself so that it has balance
        # between descriptor creation (where this is not inted) and descriptor
        # parsing (where this is inited)
        v3_desc._inner_layer = v3_desc_inner_layer

        # Check max size is within range
        if len(str(v3_desc)) > params.MAX_DESCRIPTOR_SIZE:
            logger.error("Created descriptor is too big (%d intros). Consider "
                         "relaxing number of instances or intro points per instance "
                         "(see N_INTROS_PER_INSTANCE)")
            raise BadDescriptor

        super().__init__(onion_address, v3_desc)

    def set_last_publish_attempt_ts(self, last_publish_attempt_ts):
        self.last_publish_attempt_ts = last_publish_attempt_ts

    def set_last_upload_ts(self, last_upload_ts):
        self.last_upload_ts = last_upload_ts

    def set_responsible_hsdirs(self, responsible_hsdirs):
        self.responsible_hsdirs = responsible_hsdirs

    def _recertify_intro_point(self, intro_point, descriptor_signing_key):
        """
        Given an IntroductionPointV3 object, re-certify it using the
        'descriptor_signing_key' for this new descriptor.

        Return the recertified intro point.
        """
        original_auth_key_cert = intro_point.auth_key_cert
        original_enc_key_cert = intro_point.enc_key_cert

        # We have already removed all the intros with legacy keys. Make sure that
        # no legacy intros sneaks up on us, becausey they would result in
        # unparseable descriptors if we don't recertify them (and we won't).
        assert(not intro_point.legacy_key_cert)

        # Get all the certs we need to recertify
        # [we need to use the _replace method of namedtuples because there is no
        # setter for those attributes due to the way stem sets those fields. If we
        # attempt to normally replace the attributes we get the following
        # exception: AttributeError: can't set attribute]
        recertified_intro_point = intro_point._replace(auth_key_cert=self._recertify_ed_certificate(original_auth_key_cert,
                                                                                                    descriptor_signing_key),
                                                       enc_key_cert=self._recertify_ed_certificate(original_enc_key_cert,
                                                                                                   descriptor_signing_key))

        return recertified_intro_point

    def _recertify_ed_certificate(self, ed_cert, descriptor_signing_key):
        """
        Recertify an HSv3 intro point certificate using the new descriptor signing
        key so that it can be accepted as part of a new descriptor.

        "Recertifying" means taking the certified key and signing it with a new
        key.

        Return the new certificate.
        """
        # pylint: disable=no-member
        extensions = [Ed25519Extension(ExtensionType.HAS_SIGNING_KEY, None, stem.util._pubkey_bytes(descriptor_signing_key))]
        new_cert = Ed25519CertificateV1(cert_type=ed_cert.type,
                                        expiration=ed_cert.expiration,
                                        key_type=ed_cert.key_type,
                                        key=ed_cert.key,
                                        extensions=extensions,
                                        signing_key=descriptor_signing_key)

        return new_cert

    def _get_revision_counter(self, identity_priv_key, is_first_desc):
        """
        Get the revision counter using the order-preserving-encryption scheme from
        rend-spec-v3.txt section F.2.
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance
        now = int(stem.util.datetime_to_unix(datetime.datetime.utcnow()))

        # TODO: Mention that this is done with the private key instead of the blinded priv key
        # this means that this won't cooperate with normal tor
        privkey_bytes = identity_priv_key.private_bytes(encoding=serialization.Encoding.Raw,
                                                        format=serialization.PrivateFormat.Raw,
                                                        encryption_algorithm=serialization.NoEncryption())
        cipher_key = hashlib.sha3_256(b"rev-counter-generation" + privkey_bytes).digest()

        if is_first_desc:
            srv_start = my_onionbalance.consensus.get_start_time_of_previous_srv_run()
        else:
            srv_start = my_onionbalance.consensus.get_start_time_of_current_srv_run()
        srv_start = int(srv_start)

        seconds_since_srv_start = now - srv_start
        # This must be strictly positive
        seconds_since_srv_start += 1

        ope_result = sum(w for w, _ in zip(self._get_ope_scheme_words(cipher_key),
                                           range(seconds_since_srv_start)))

        logger.debug("Rev counter for %s descriptor (SRV secs %s, OPE %s)",
                     "first" if is_first_desc else "second",
                     seconds_since_srv_start, ope_result)

        return ope_result

    def _get_ope_scheme_words(self, cipher_key):
        IV = b'\x00' * 16

        cipher = Cipher(algorithms.AES(cipher_key), modes.CTR(IV), backend=backend)
        e = cipher.encryptor()
        while True:
            v = e.update(b'\x00\x00')
            yield v[0] + 256 * v[1] + 1


class ReceivedDescriptor(V3Descriptor):
    """
    An instance v3 descriptor received from the network.

    This class supports parsing descriptors.
    """

    def __init__(self, desc_text, onion_address):
        """
        Parse a descriptor in 'desc_text' and return an ReceivedDescriptor object.

        Raises BadDescriptor if the descriptor cannot be used.
        """
        try:
            v3_desc = HiddenServiceDescriptorV3.from_str(desc_text)
            v3_desc.decrypt(onion_address)
        except ValueError as err:
            logger.warning("Descriptor is corrupted (%s).", err)
            raise BadDescriptor

        self.received_ts = datetime.datetime.utcnow()

        logger.debug("Successfuly decrypted descriptor for %s!", onion_address)

        super().__init__(onion_address, v3_desc)

    def is_old(self):
        """
        Return True if this received descriptor is old and we should consider the
        instance as offline.
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        received_age = datetime.datetime.utcnow() - self.received_ts
        received_age = received_age.total_seconds()

        if my_onionbalance.is_testnet:
            too_old_threshold = params.INSTANCE_DESCRIPTOR_TOO_OLD_TESTNET
        else:
            too_old_threshold = params.INSTANCE_DESCRIPTOR_TOO_OLD

        if received_age > too_old_threshold:
            return True

        return False


class BadDescriptor(Exception):
    pass
