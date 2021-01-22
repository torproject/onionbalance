# -*- coding: utf-8 -*-
import base64
import textwrap
import datetime

import Cryptodome.Signature.pkcs1_15
import Cryptodome.Hash.SHA

import stem.descriptor.hidden_service_descriptor

from onionbalance.hs_v2 import util

from onionbalance.common import log
from onionbalance.hs_v2 import config

logger = log.get_logger()


def generate_service_descriptor(permanent_key, introduction_point_list=None,
                                replica=0, timestamp=None, deviation=0):
    """
    High-level interface for generating a signed HS descriptor
    """

    if not timestamp:
        timestamp = datetime.datetime.utcnow()
    unix_timestamp = int(timestamp.strftime("%s"))

    permanent_key_block = make_public_key_block(permanent_key)
    permanent_id = util.calc_permanent_id(permanent_key)

    # Calculate the current secret-id-part for this hidden service
    # Deviation allows the generation of a descriptor for a different time
    # period.
    time_period = (util.get_time_period(unix_timestamp, permanent_id) + int(deviation))

    secret_id_part = util.calc_secret_id_part(time_period, None, replica)
    descriptor_id = util.calc_descriptor_id(permanent_id, secret_id_part)

    if not introduction_point_list:
        onion_address = util.calc_onion_address(permanent_key)
        raise ValueError("No introduction points for service %s.onion." %
                         onion_address)

    # Generate the introduction point section of the descriptor
    intro_section = make_introduction_points_part(
        introduction_point_list
    )

    unsigned_descriptor = generate_hs_descriptor_raw(
        desc_id_base32=util.base32_encode_str(descriptor_id),
        permanent_key_block=permanent_key_block,
        secret_id_part_base32=util.base32_encode_str(secret_id_part),
        publication_time=util.rounded_timestamp(timestamp),
        introduction_points_part=intro_section
    )

    signed_descriptor = sign_descriptor(unsigned_descriptor, permanent_key)
    return signed_descriptor


def generate_hs_descriptor_raw(desc_id_base32, permanent_key_block,
                               secret_id_part_base32, publication_time,
                               introduction_points_part):
    """
    Generate hidden service descriptor string
    """
    doc = [
        "rendezvous-service-descriptor {}".format(desc_id_base32),
        "version 2",
        "permanent-key",
        permanent_key_block,
        "secret-id-part {}".format(secret_id_part_base32),
        "publication-time {}".format(publication_time),
        "protocol-versions 2,3",
        "introduction-points",
        introduction_points_part,
        "signature\n",
    ]

    unsigned_descriptor = '\n'.join(doc)
    return unsigned_descriptor


def make_introduction_points_part(introduction_point_list=None):
    """
    Make introduction point block from list of IntroductionPoint objects
    """

    # If no intro points were specified, we should create an empty list
    if not introduction_point_list:
        introduction_point_list = []

    intro = []
    for intro_point in introduction_point_list:
        intro.append("introduction-point {}".format(intro_point.identifier))
        intro.append("ip-address {}".format(intro_point.address))
        intro.append("onion-port {}".format(intro_point.port))
        intro.append("onion-key")
        intro.append(intro_point.onion_key)
        intro.append("service-key")
        intro.append(intro_point.service_key)

    intro_section = '\n'.join(intro).encode('utf-8')
    intro_section_base64 = base64.b64encode(intro_section).decode('utf-8')
    intro_section_base64 = textwrap.fill(intro_section_base64, 64)

    # Add the header and footer:
    intro_points_with_headers = '\n'.join([
        '-----BEGIN MESSAGE-----',
        intro_section_base64,
        '-----END MESSAGE-----'])
    return intro_points_with_headers


def make_public_key_block(key):
    """
    Get ASN.1 representation of public key, base64 and add headers
    """
    asn1_pub = util.get_asn1_sequence(key)
    pub_base64 = base64.b64encode(asn1_pub).decode('utf-8')
    pub_base64 = textwrap.fill(pub_base64, 64)

    # Add the header and footer:
    pub_with_headers = '\n'.join([
        '-----BEGIN RSA PUBLIC KEY-----',
        pub_base64,
        '-----END RSA PUBLIC KEY-----'])
    return pub_with_headers

def pad_msg_with_tor_pkcs(msg_hash, emLen, with_hash_parameters=True):
    """
    Tor requires PKCS#1 1.5 padding for descriptor signatures but does not
    include the algorithmIdentifier as specified in RFC3447.

    Unfortunately, most crypto libraries add that algorithmIdentifier by force
    and hence we need this function for monkey patching.
    """
    digestInfo = msg_hash.digest()
    PS = b'\xFF' * (emLen - len(digestInfo) - 3)
    return b'\x00\x01' + PS + b'\x00' + digestInfo

def sign(body, private_key):
    """
    Sign, base64 encode, wrap and add Tor signature headers

    The message digest is PKCS1 padded without the optional
    algorithmIdentifier section.
    """
    # First monkey-patch cryptodome to do the Tor PKCS#1 padding
    Cryptodome.Signature.pkcs1_15._EMSA_PKCS1_V1_5_ENCODE = pad_msg_with_tor_pkcs

    # The RSA signing API requires a hasher as input
    hasher = Cryptodome.Hash.SHA1.new(body)
    # Now do the signing
    signer = Cryptodome.Signature.pkcs1_15.new(private_key)
    signature_bytes = signer.sign(hasher)

    # Convert the signature to the base64 format that our descriptors like
    signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')
    signature_base64 = textwrap.fill(signature_base64, 64)

    # Add the header and footer:
    signature_with_headers = '\n'.join([
        '-----BEGIN SIGNATURE-----',
        signature_base64,
        '-----END SIGNATURE-----'])
    return signature_with_headers


def sign_descriptor(descriptor, service_privkey):
    """
    Sign or resign a provided hidden service descriptor
    """
    token_descriptor_signature = '\nsignature\n'

    # Remove signature block if it exists
    if token_descriptor_signature in descriptor:
        descriptor = descriptor[:descriptor.find(token_descriptor_signature) + len(token_descriptor_signature)]
    else:
        descriptor = descriptor.strip() + token_descriptor_signature

    signature_with_headers = sign(descriptor.encode('utf-8'), service_privkey)
    return descriptor + signature_with_headers

def descriptor_received(descriptor_content):
    """
    Process onion service descriptors retrieved from the HSDir system or
    received directly over the metadata channel.
    """

    try:
        parsed_descriptor = stem.descriptor.hidden_service_descriptor.\
            HiddenServiceDescriptor(descriptor_content, validate=True)
    except ValueError:
        logger.exception("Received an invalid service descriptor.")
        return None

    # Ensure the received descriptor matches the requested descriptor
    permanent_key = Cryptodome.PublicKey.RSA.importKey(
        parsed_descriptor.permanent_key)
    descriptor_onion_address = util.calc_onion_address(permanent_key)

    known_descriptor, instance_changed = False, False
    for instance in [instance for service in config.services for
                     instance in service.instances]:
        if instance.onion_address == descriptor_onion_address:
            instance_changed |= instance.update_descriptor(parsed_descriptor)
            known_descriptor = True

    if instance_changed:
        logger.info("The introduction point set has changed for instance "
                    "%s.onion.", descriptor_onion_address)

    if not known_descriptor:
        # No matching service instance was found for the descriptor
        logger.debug("Received a descriptor for an unknown service:\n%s",
                     descriptor_content.decode('utf-8'))
        logger.warning("Received a descriptor with address %s.onion that "
                       "did not match any configured service instances.",
                       descriptor_onion_address)

    return None
