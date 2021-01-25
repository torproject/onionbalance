import datetime
import base64
import hashlib

import stem
import stem.util
import stem.descriptor.remote
from stem.descriptor.networkstatus import NetworkStatusDocumentV3

from onionbalance.common import log
from onionbalance.hs_v3 import tor_node

logger = log.get_logger()


class Consensus(object):
    """
    This represents a consensus object.

    It's initialized once in startup and refreshed during the runtime using the
    refresh() method to get the latest consensus.
    """

    def __init__(self, do_refresh_consensus=True):
        # A list of tor_node:Node objects contained in the current consensus
        self.nodes = None
        # A stem NetworkStatusDocumentV3 object representing the current consensus
        self.consensus = None

        if not do_refresh_consensus:
            return

        # Set self.consensus to a NetworkStatusDocumentV3 object
        # and initialize the nodelist
        self.refresh()

    def refresh(self):
        """
        Attempt to refresh the consensus with the latest one available.
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        # Fetch the current md consensus from the control port
        md_consensus_str = my_onionbalance.controller.get_md_consensus().encode()
        try:
            self.consensus = NetworkStatusDocumentV3(md_consensus_str)
        except ValueError:
            logger.warning("No valid consensus received. Waiting for one...")
            return

        # Check if it's live
        if not self.is_live():
            logger.info("Loaded consensus is not live. Waiting for a live one.")
            return

        self.nodes = self._initialize_nodes()

    def get_routerstatuses(self):
        """Give access to the routerstatus entries in this consensus"""

        # We should never be asked for routerstatuses with a non-live consensus
        # so make sure this is the case.
        assert(self.is_live())

        return self.consensus.routers

    def is_live(self):
        """
        Return True if the consensus is live.

        This function replicates the behavior of the little-t-tor
        networkstatus_get_reasonably_live_consensus() function.
        """
        if not self.consensus:
            return False

        REASONABLY_LIVE_TIME = 24 * 60 * 60
        now = datetime.datetime.utcnow()

        return now >= self.consensus.valid_after - datetime.timedelta(seconds=REASONABLY_LIVE_TIME) and \
            now <= self.consensus.valid_until + datetime.timedelta(seconds=REASONABLY_LIVE_TIME)

    def _initialize_nodes(self):
        """
        Initialize self.nodes with the list of current nodes.
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        nodes = []

        try:
            microdescriptors_list = list(my_onionbalance.controller.controller.get_microdescriptors())
        except stem.DescriptorUnavailable:
            logger.warning("Can't get microdescriptors from Tor. Delaying...")
            return

        # Turn the mds into a dictionary indexed by the digest as an
        # optimization while matching them with routerstatuses.
        microdescriptors_dict = {}
        for md in microdescriptors_list:
            microdescriptors_dict[md.digest()] = md

        # Go through the routerstatuses and match them up with
        # microdescriptors, and create a Node object for each match. If there
        # is no match we don't register it as a node.
        for relay_fpr, relay_routerstatus in self.get_routerstatuses().items():
            logger.debug("Checking routerstatus with md digest %s", relay_routerstatus.microdescriptor_digest)

            # Skip routerstatuses for which we cannot find a microdescriptor
            if relay_routerstatus.microdescriptor_digest not in microdescriptors_dict:
                logger.debug("Could not find microdesc for rs with fpr %s", relay_fpr)
                continue

            node_microdescriptor = microdescriptors_dict[relay_routerstatus.microdescriptor_digest]
            node = tor_node.Node(node_microdescriptor, relay_routerstatus)
            nodes.append(node)

        logger.debug("Initialized %d nodes (%d routerstatuses / %d microdescriptors)",
                     len(nodes), len(self.get_routerstatuses()), len(microdescriptors_list))

        return nodes

    def _get_disaster_srv(self, time_period_num):
        """
        Return disaster SRV for 'time_period_num'.
        """
        time_period_length = self.get_time_period_length()

        disaster_body = b"shared-random-disaster" + time_period_length.to_bytes(8, 'big') + time_period_num.to_bytes(8, 'big')
        return hashlib.sha3_256(disaster_body).digest()

    def get_current_srv(self, time_period_num):
        if self.consensus.shared_randomness_current_value:
            return base64.b64decode(self.consensus.shared_randomness_current_value)
        elif time_period_num:
            logger.info("SRV not found so falling back to disaster mode")
            return self._get_disaster_srv(time_period_num)
        else:
            return None

    def get_previous_srv(self, time_period_num):
        if self.consensus.shared_randomness_previous_value:
            return base64.b64decode(self.consensus.shared_randomness_previous_value)
        elif time_period_num:
            logger.info("SRV not found so falling back to disaster mode")
            return self._get_disaster_srv(time_period_num)
        else:
            return None

    def _get_srv_phase_duration(self):
        """
        Return the length of the phase of a shared random protocol run in minutes.
        """

        # Each SRV phase takes 12 rounds. But the duration of the round depends
        # on how big the voting rounds are which differs between live and
        # testing network:
        from onionbalance.hs_v3.onionbalance import my_onionbalance
        if my_onionbalance.is_testnet:
            return (12 * 20) // 60
        else:
            return 12 * 60

    def get_time_period_length(self):
        """
        Get the HSv3 time period length in minutes
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance
        if my_onionbalance.is_testnet:
            # This is a chutney network! Use hs_common.c:get_time_period_length()
            # logic to calculate time period length
            return (24 * 20) // 60
        else:
            # This is not a chutney network, so time period length is 1440 minutes (24 hours)
            return 24 * 60

    def get_blinding_param(self, identity_pubkey, time_period_number):
        """
        Calculate the HSv3 blinding parameter as specified in rend-spec-v3.txt section A.2:

         h = H(BLIND_STRING | A | s | B | N)
         BLIND_STRING = "Derive temporary signing key" | INT_1(0)
         N = "key-blind" | INT_8(period-number) | INT_8(period_length)
         B = "(1511[...]2202, 4631[...]5960)"

        Use the time period number in 'time_period_number'.
        """
        ED25519_BASEPOINT = b"(15112221349535400772501151409588531511" \
            b"454012693041857206046113283949847762202, " \
            b"463168356949264781694283940034751631413" \
            b"07993866256225615783033603165251855960)"
        BLIND_STRING = b"Derive temporary signing key" + bytes([0])

        period_length = self.get_time_period_length()
        N = b"key-blind" + time_period_number.to_bytes(8, 'big') + period_length.to_bytes(8, 'big')

        return hashlib.sha3_256(BLIND_STRING + identity_pubkey + ED25519_BASEPOINT + N).digest()

    def get_next_time_period_num(self, valid_after=None):
        return self.get_time_period_num(valid_after) + 1

    def get_time_period_num(self, valid_after=None):
        """
        Get time period number for this 'valid_after'.

        valid_after is a datetime (if not set, we get it ourselves)
        time_period_length set to default value of 1440 minutes == 1 day
        """
        if not valid_after:
            assert(self.is_live())
            valid_after = self.consensus.valid_after
            valid_after = stem.util.datetime_to_unix(valid_after)

        time_period_length = self.get_time_period_length()

        seconds_since_epoch = valid_after
        minutes_since_epoch = seconds_since_epoch // 60

        # Calculate offset as specified in rend-spec-v3.txt [TIME-PERIODS]
        time_period_rotation_offset = self._get_srv_phase_duration()

        assert(minutes_since_epoch > time_period_rotation_offset)
        minutes_since_epoch -= time_period_rotation_offset

        time_period_num = minutes_since_epoch // time_period_length
        return int(time_period_num)

    def get_start_time_of_current_srv_run(self):
        """
        Return the start time of the current SR protocol run using the times from
        the current consensus. For example, if the latest consensus valid-after is
        23/06/2017 23:00:00 and a full SR protocol run is 24 hours, this function
        returns 23/06/2017 00:00:00.

        TODO: unittest
        """
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        assert(self.is_live())

        beginning_of_current_round = stem.util.datetime_to_unix(self.consensus.valid_after)

        # Voting interval is 20 secs in chutney and one hour in real network
        if my_onionbalance.is_testnet:
            voting_interval_secs = 20
        else:
            voting_interval_secs = 60 * 60

        # Get current SR protocol round (an SR protocol run has 24 rounds)
        curr_round_slot = (beginning_of_current_round // voting_interval_secs) % 24
        time_elapsed_since_start_of_run = curr_round_slot * voting_interval_secs

        logger.debug("Current SRV proto run: Start of current round: %s. "
                     "Time elapsed: %s (%s)", beginning_of_current_round,
                     time_elapsed_since_start_of_run, voting_interval_secs)

        return int(beginning_of_current_round - time_elapsed_since_start_of_run)

    def get_start_time_of_previous_srv_run(self):
        from onionbalance.hs_v3.onionbalance import my_onionbalance

        start_time_of_current_run = self.get_start_time_of_current_srv_run()
        if my_onionbalance.is_testnet:
            return start_time_of_current_run - 24 * 20
        else:
            return start_time_of_current_run - 24 * 3600

    def get_start_time_of_next_time_period(self, valid_after=None):
        """
        Return the start time of the upcoming time period
        """
        assert(self.is_live())

        # Get start time of next time period
        time_period_length = self.get_time_period_length()
        next_time_period_num = self.get_next_time_period_num(valid_after)
        start_of_next_tp_in_mins = next_time_period_num * time_period_length

        # Apply rotation offset as specified by prop224 section [TIME-PERIODS]
        time_period_rotation_offset = self._get_srv_phase_duration()

        return (start_of_next_tp_in_mins + time_period_rotation_offset) * 60


class NoLiveConsensus(Exception):
    pass
