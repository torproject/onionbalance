import base64
import bisect
import hashlib

import stem.util

from onionbalance.common import log

from onionbalance.hs_v3 import tor_node
from onionbalance.hs_v3 import params

logger = log.get_logger()


def _time_between_tp_and_srv(valid_after):
    """
     Return True if we are currently in the time segment between a new time
     period and a new SRV (in the real network that happens between 12:00 and
     00:00 UTC). Here is a diagram showing exactly when this returns true:

        +------------------------------------------------------------------+
        |                                                                  |
        | 00:00      12:00       00:00       12:00       00:00       12:00 |
        | SRV#1      TP#1        SRV#2       TP#2        SRV#3       TP#3  |
        |                                                                  |
        |  $==========|-----------$===========|-----------$===========|    |
        |             ^^^^^^^^^^^^            ^^^^^^^^^^^^                 |
        |                                                                  |
        +------------------------------------------------------------------+
    """
    from onionbalance.hs_v3.onionbalance import my_onionbalance

    srv_start_time = my_onionbalance.consensus.get_start_time_of_current_srv_run()
    tp_start_time = my_onionbalance.consensus.get_start_time_of_next_time_period(srv_start_time)
    valid_after = stem.util.datetime_to_unix(valid_after)

    if valid_after >= srv_start_time and valid_after < tp_start_time:
        logger.debug("We are between SRV and TP")
        return False

    logger.debug("We are between TP and SRV (valid_after: %s, srv_start_time: %s -> tp_start_time: %s)",
                 valid_after, srv_start_time, tp_start_time)
    return True


def get_srv_and_time_period(is_first_descriptor):
    """
    Return SRV and time period based on current consensus time
    """
    from onionbalance.hs_v3.onionbalance import my_onionbalance

    valid_after = my_onionbalance.consensus.consensus.valid_after

    current_tp = my_onionbalance.consensus.get_time_period_num()
    previous_tp = current_tp - 1
    next_tp = current_tp + 1
    assert(previous_tp > 0)

    # Get the right TP/SRV
    if is_first_descriptor:
        if _time_between_tp_and_srv(valid_after):
            srv = my_onionbalance.consensus.get_previous_srv(previous_tp)
            tp = previous_tp
            _case = 1  # just for debugging
        else:
            srv = my_onionbalance.consensus.get_previous_srv(current_tp)
            tp = current_tp
            _case = 2  # just for debugging
    else:
        if _time_between_tp_and_srv(valid_after):
            srv = my_onionbalance.consensus.get_current_srv(current_tp)
            tp = current_tp
            _case = 3  # just for debugging
        else:
            srv = my_onionbalance.consensus.get_current_srv(next_tp)
            tp = next_tp
            _case = 4  # just for debugging

    srv_b64 = base64.b64encode(srv) if srv else None
    logger.debug("For valid_after %s we got SRV %s and TP %s (case: #%d)",
                 valid_after, srv_b64, tp, _case)

    return srv, tp


def _get_hash_ring_for_descriptor(is_first_descriptor):
    """
    Return a dictionary { <node hsdir index> : Node , .... }
    """
    from onionbalance.hs_v3.onionbalance import my_onionbalance

    node_hash_ring = {}

    srv, time_period_num = get_srv_and_time_period(is_first_descriptor)
    logger.info("Using srv %s and TP#%s (%s descriptor)",
                srv.hex(), time_period_num,
                "first" if is_first_descriptor else "second")

    for node in my_onionbalance.consensus.nodes:
        try:
            hsdir_index = node.get_hsdir_index(srv, time_period_num)
        except (tor_node.NoEd25519Identity, tor_node.NoHSDir) as e:
            logger.debug("Could not find ed25519 for node %s (%s)", node.routerstatus.fingerprint, e)
            continue

        logger.debug("%s: Node: %s,  index: %s", is_first_descriptor, node.get_hex_fingerprint(), hsdir_index.hex())
        node_hash_ring[hsdir_index] = node

    return node_hash_ring


def _get_hidden_service_index(blinded_pubkey, replica_num, is_first_descriptor):
    """
        hs_index(replicanum) = H("store-at-idx" |
                                 blinded_public_key |
                                 INT_8(replicanum) |
                                 INT_8(period_length) |
                                 INT_8(period_num) )
    """
    from onionbalance.hs_v3.onionbalance import my_onionbalance
    period_length = my_onionbalance.consensus.get_time_period_length()

    replica_num_int_8 = replica_num.to_bytes(8, 'big')
    period_length_int_8 = (period_length).to_bytes(8, 'big')

    _, time_period_num = get_srv_and_time_period(is_first_descriptor)
    logger.info("Getting HS index with TP#%s for %s descriptor (%d replica) ",
                time_period_num,
                "first" if is_first_descriptor else "second", replica_num)
    period_num_int_8 = time_period_num.to_bytes(8, 'big')

    hash_body = b"%s%s%s%s%s" % (b"store-at-idx",
                                 blinded_pubkey,
                                 replica_num_int_8,
                                 period_length_int_8,
                                 period_num_int_8)

    hs_index = hashlib.sha3_256(hash_body).digest()

    return hs_index


def get_responsible_hsdirs(blinded_pubkey, is_first_descriptor):
    """
    Return a list with the responsible HSDirs for a service with 'blinded_pubkey'.

    The returned list is a list of fingerprints.
    """
    from onionbalance.hs_v3.onionbalance import my_onionbalance

    # Always use a live consensus when calculating responsible HSDirs
    assert(my_onionbalance.consensus.is_live())

    responsible_hsdirs = []

    # TODO: Improve representation of hash ring here... No need to go
    # between list and dictionary...

    # dictionary { <node hsdir index> : Node , .... }
    node_hash_ring = _get_hash_ring_for_descriptor(is_first_descriptor)
    if not node_hash_ring:
        raise EmptyHashRing

    sorted_hash_ring_list = sorted(list(node_hash_ring.keys()))

    logger.info("Initialized hash ring of size %d (blinded key: %s)",
                len(node_hash_ring), base64.b64encode(blinded_pubkey))

    for replica_num in range(1, params.HSDIR_N_REPLICAS + 1):
        # The HSDirs that we are gonna store this replica in
        replica_store_hsdirs = []

        hidden_service_index = _get_hidden_service_index(blinded_pubkey, replica_num, is_first_descriptor)

        # Find position of descriptor ID in the HSDir list
        index = bisect.bisect_left(sorted_hash_ring_list, hidden_service_index)

        logger.info("\t Tried with HS index %s got position %d", hidden_service_index.hex(), index)

        while len(replica_store_hsdirs) < params.HSDIR_SPREAD_STORE:
            try:
                hsdir_key = sorted_hash_ring_list[index]
                index += 1
            except IndexError:
                # Wrap around when we reach the end of the HSDir list
                index = 0
                hsdir_key = sorted_hash_ring_list[index]

            hsdir_node = node_hash_ring[hsdir_key]

            # Check if we have already added this node to this
            # replica. This should never happen on the real network but
            # might happen in small testnets like chutney!
            if hsdir_node.get_hex_fingerprint() in replica_store_hsdirs:
                logger.debug("Ignoring already added HSDir to this replica!")
                break

            # Check if we have already added this node to the responsible
            # HSDirs. This can happen in the second replica and we should
            # skip the node
            if hsdir_node.get_hex_fingerprint() in responsible_hsdirs:
                logger.debug("Ignoring already added HSDir!")
                continue

            logger.debug("%d: %s: %s", index, hsdir_node.get_hex_fingerprint(), hsdir_key.hex())

            replica_store_hsdirs.append(hsdir_node.get_hex_fingerprint())

        responsible_hsdirs.extend(replica_store_hsdirs)

    # Do a sanity check
    if my_onionbalance.is_testnet:
        # If we are on chutney it's normal to not have enough nodes to populate the hashring
        assert(len(responsible_hsdirs) <= params.HSDIR_N_REPLICAS * params.HSDIR_SPREAD_STORE)
    else:
        if (len(responsible_hsdirs) != params.HSDIR_N_REPLICAS * params.HSDIR_SPREAD_STORE):
            logger.critical("Got the wrong number of responsible HSDirs: %d. Aborting", len(responsible_hsdirs))
            raise EmptyHashRing

    return responsible_hsdirs


class EmptyHashRing(Exception):
    pass
