import datetime
import unittest
import mock
from types import SimpleNamespace

from onionbalance.hs_v3 import consensus

from onionbalance.hs_v3.onionbalance import Onionbalance

class DummyConsensus(consensus.Consensus):
    def __init__(self):
        self.consensus = None

class OutdatedConsensus(unittest.TestCase):
    def test_outdated_consensus(self):
        current_time = datetime.datetime.fromtimestamp(10101010101)

        consensus = DummyConsensus()

        consensus.consensus = mock.Mock()
        with mock.patch("datetime.datetime") as mock_datetime:
            consensus.consensus.valid_after = current_time
            # valid_until is 3 hours in the future
            consensus.consensus.valid_until = current_time + datetime.timedelta(seconds=3600 * 3)

            # Test some legitimate cases
            mock_datetime.utcnow.return_value = current_time
            self.assertTrue(consensus.is_live())

            mock_datetime.utcnow.return_value = current_time + datetime.timedelta(seconds=3600 * 11)
            self.assertTrue(consensus.is_live())

            mock_datetime.utcnow.return_value = current_time + datetime.timedelta(seconds=3600 * 12)
            self.assertTrue(consensus.is_live())

            mock_datetime.utcnow.return_value = current_time + datetime.timedelta(seconds=3600 * 24)
            self.assertTrue(consensus.is_live())

            mock_datetime.utcnow.return_value = current_time - datetime.timedelta(seconds=3600 * 24)
            self.assertTrue(consensus.is_live())

            # Now test some bad cases. The is_live() function is lenient up to 24
            # hours after the valid_until, or 24 hours before the valid_after
            mock_datetime.utcnow.return_value = consensus.consensus.valid_until + datetime.timedelta(seconds=3600 * 24 + 1)
            self.assertFalse(consensus.is_live())

            mock_datetime.utcnow.return_value = consensus.consensus.valid_after - datetime.timedelta(seconds=3600 * 24 + 1)
            self.assertFalse(consensus.is_live())

class TestReloadConfig(unittest.TestCase):

    @mock.patch('onionbalance.hs_v3.service.OnionbalanceService')
    @mock.patch('onionbalance.hs_v3.consensus.Consensus')
    @mock.patch('onionbalance.hs_v3.stem_controller.StemController')
    @mock.patch('onionbalance.hs_v3.onionbalance.Onionbalance.load_config_file')
    @mock.patch('onionbalance.hs_v3.manager.init_scheduler')
    def test_reload_config(self, mock_init_scheduler, mock_load_config_file, mock_StemController, mock_Consensus, mock_OnionbalanceService):
        # setup onionbalance instance
        test_onionbalance = Onionbalance()
        test_onionbalance.args = self.create_dummy_args()

        # checks if Onionbalance.load_config_file and manager.init_scheduler have been called by reload_config
        test_onionbalance.reload_config()
        mock_load_config_file.assert_called_once()
        mock_init_scheduler.assert_called_once()

    @staticmethod
    def create_dummy_args():
        return SimpleNamespace(config='config/config.yaml', ip='127.0.0.1', is_testnet=False, port=6666, socket='/var/run/tor/control', verbosity='info')
