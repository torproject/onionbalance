import unittest
import mock
from types import SimpleNamespace

from onionbalance.hs_v3.onionbalance import Onionbalance

class TestReloadConfig(unittest.TestCase):

    @mock.patch('onionbalance.hs_v3.service.OnionBalanceService')
    @mock.patch('onionbalance.hs_v3.consensus.Consensus')
    @mock.patch('onionbalance.hs_v3.stem_controller.StemController')
    @mock.patch('onionbalance.hs_v3.onionbalance.Onionbalance.load_config_file')
    @mock.patch('onionbalance.hs_v3.manager.init_scheduler')
    def test_reload_config(self, mock_init_scheduler, mock_load_config_file, mock_StemController, mock_Consensus, mock_OnionBalanceService):
        # setup onionbalance instance
        test_onionbalance = Onionbalance()
        test_onionbalance.args = self.create_dummy_args()

        # checks if Onionbalance.load_config_file and manager.init_scheduler have been called by reload_config
        test_onionbalance.reload_config()
        mock_load_config_file.assert_called_once()
        mock_init_scheduler.assert_called_once()

    @staticmethod
    def create_dummy_args():
        return SimpleNamespace(config='config/config.yaml', hs_version='v3', ip='127.0.0.1', is_testnet=False, port=6666, socket='/var/run/tor/control', verbosity='info')