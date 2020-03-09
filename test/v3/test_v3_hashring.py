import unittest
import mock
import datetime
import base64

from cryptography.hazmat.primitives.asymmetric import ed25519

from onionbalance.hs_v3 import tor_node
from onionbalance.hs_v3 import hashring
from onionbalance.hs_v3 import consensus

CORRECT_HSDIR_FPRS_FIRST_DESCRIPTOR = [
    "D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1",
    "2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F2F",
    "B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0",
    "3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A3A",
    "5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A",
    "DFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDF",
    "F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7F7",
    "3434343434343434343434343434343434343434" ]

CORRECT_HSDIR_FPRS_SECOND_DESCRIPTOR = [
    "5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D5D",
    "9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A9A",
    "D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1D1",
    "7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A7A",
    "C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3C3",
    "C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6C6",
    "E9E9E9E9E9E9E9E9E9E9E9E9E9E9E9E9E9E9E9E9",
    "8686868686868686868686868686868686868686"
]

class DummyConsensus(consensus.Consensus):
    def __init__(self):
        self.consensus = None


class TestHashRing(unittest.TestCase):
    def test_hashring(self):
        current_time = datetime.datetime.fromtimestamp(10101010101)
        current_srv = bytes([41])*32
        previous_srv = bytes([42])*32

        # Create 255 fake Tor nodes that will be used as part of the unittest
        network_nodes = []
        for i in range(1,256):
            microdescriptor = mock.Mock()
            routerstatus = mock.Mock()

            routerstatus.fingerprint = (bytes([i])*20).hex()
            routerstatus.protocols = {'HSDir' : [2]}
            routerstatus.flags = ['HSDir']
            node_ed25519_id_b64 = base64.b64encode(bytes([i])*32).decode('utf-8')
            microdescriptor.identifiers = {'ed25519' : node_ed25519_id_b64}
            node = tor_node.Node(microdescriptor, routerstatus)
            network_nodes.append(node)

        # Mock a fake consensus
        consensus = DummyConsensus()
        consensus.consensus = mock.Mock()
        consensus.consensus.valid_after = current_time
        consensus.get_current_srv = mock.Mock()
        consensus.get_current_srv.return_value = current_srv
        consensus.get_previous_srv = mock.Mock()
        consensus.get_previous_srv.return_value = previous_srv
        consensus.is_live = mock.Mock()
        consensus.is_live.return_value = True
        consensus.nodes = network_nodes

        # Mock a fake Tor network
        from onionbalance.hs_v3.onionbalance import my_onionbalance
        my_onionbalance.consensus = consensus

        previous_blinded_pubkey_hex = "063AEC5E1FD3025098F2DF71EF570B28D94B463FFCCB5EC6A9C061E38F551C6A"
        previous_blinded_pubkey_bytes = base64.b16decode(previous_blinded_pubkey_hex)

        responsible_hsdirs = hashring.get_responsible_hsdirs(previous_blinded_pubkey_bytes, True)

        i = 0
        for responsible_hsdir in responsible_hsdirs:
            self.assertEqual(responsible_hsdir.upper(), CORRECT_HSDIR_FPRS_FIRST_DESCRIPTOR[i])
            i+=1

        print("===")

        # we need to use the new blinded key since this uses a new time period.........
        current_blinded_pubkey_hex = "5DB624F2D74F103E6E8C6FBCCD074586EF5A5572F90673C00B77DEF94EC11499"
        current_blinded_pubkey_bytes = base64.b16decode(current_blinded_pubkey_hex)

        responsible_hsdirs = hashring.get_responsible_hsdirs(current_blinded_pubkey_bytes, False)

        i = 0
        for responsible_hsdir in responsible_hsdirs:
            self.assertEqual(responsible_hsdir.upper(), CORRECT_HSDIR_FPRS_SECOND_DESCRIPTOR[i])
            i+=1

if __name__ == '__main__':
    unittest.main()
