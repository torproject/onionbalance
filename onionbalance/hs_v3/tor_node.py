import base64

import hashlib

from onionbalance.common import log

logger = log.get_logger()


class Node(object):
    """
    Represents a Tor node.

    A Node instance gets created for each node of a consensus. When we fetch a
    new consensus, we create new Node instances for the routers found inside.

    The 'microdescriptor' and 'routerstatus' fields of this object are
    immutable: They are set once when we receive the consensus based on the
    state of the network at that point, and they stay like that until we get a
    new consensus.
    """

    def __init__(self, microdescriptor, routerstatus):
        assert(microdescriptor and routerstatus)

        logger.debug("Initializing node with fpr %s", routerstatus.fingerprint)

        # The microdescriptor of this node
        self.microdescriptor = microdescriptor
        # The consensus routerstatus for this node
        self.routerstatus = routerstatus

    def get_hex_fingerprint(self):
        return self.routerstatus.fingerprint

    def get_hsdir_index(self, srv, period_num):
        """
        Get the HSDir index for this node:

           hsdir_index(node) = H("node-idx" | node_identity |
                                 shared_random_value |
                                 INT_8(period_num) |
                                 INT_8(period_length) )

        Raises NoHSDir or NoEd25519Identity in case of errors.
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        # See if this node can be an HSDir (it needs to be supported both in
        # protover and in flags)
        if 'HSDir' not in self.routerstatus.protocols or \
           2 not in self.routerstatus.protocols['HSDir'] or \
           'HSDir' not in self.routerstatus.flags:
            raise NoHSDir

        # See if ed25519 identity is supported for this node
        if 'ed25519' not in self.microdescriptor.identifiers:
            raise NoEd25519Identity

        # In stem the ed25519 identity is a base64 string and we need to add
        # the missing padding so that the python base64 module can successfuly
        # decode it.
        # TODO: Abstract this into its own function...
        ed25519_node_identity_b64 = self.microdescriptor.identifiers['ed25519']
        missing_padding = len(ed25519_node_identity_b64) % 4
        ed25519_node_identity_b64 += '=' * missing_padding
        ed25519_node_identity = base64.b64decode(ed25519_node_identity_b64)

        period_num_int_8 = period_num.to_bytes(8, 'big')
        period_length = my_onionbalance.consensus.get_time_period_length()
        period_length_int_8 = period_length.to_bytes(8, 'big')

        hash_body = b"%s%s%s%s%s" % (b"node-idx",
                                     ed25519_node_identity,
                                     srv,
                                     period_num_int_8, period_length_int_8)
        hsdir_index = hashlib.sha3_256(hash_body).digest()

        return hsdir_index


class NoEd25519Identity(Exception):
    pass


class NoHSDir(Exception):
    pass
