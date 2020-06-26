# -*- coding: utf-8 -*-
import os
import signal
import sys
import time

import Crypto.PublicKey.RSA
import pexpect

import onionbalance.hs_v2.util
from .util import parse_chutney_enviroment, create_test_config_file_v3, update_test_config_file_v3, random_onionv3_address

def test_sighup_reload_config(tmpdir):
    """
    Functional test to run OnionBalance, publish a master descriptor and
    check that it can be retrieved from the DHT.
    """

    chutney_config = parse_chutney_enviroment()

    original_instance_address = random_onionv3_address()
    config_file_path = create_test_config_file_v3(tmppath=tmpdir, instance_address=original_instance_address)
    assert config_file_path

    # Start an OnionBalance server and monitor for correct output with pexpect
    server = pexpect.spawnu("onionbalance",
                            args=[
                                '--hs-version', 'v3',
                                '-i', chutney_config.get('client_ip'),
                                '-p', str(chutney_config.get('control_port')),
                                '-c', config_file_path,
                                '-v', 'debug',
                                '--is-testnet'
                            ], logfile=sys.stdout, timeout=5)
    time.sleep(1)

    # Check for expected output from OnionBalance
    server.expect(u"Loaded the config file")
    server.expect(original_instance_address)

    # Update config file and send SIGHUP
    updated_instance_address = random_onionv3_address()
    config_file_path = update_test_config_file_v3(tmppath=tmpdir, instance_address=updated_instance_address)
    assert config_file_path
    server.kill(signal.SIGHUP)
    server.expect(u"Signal SIGHUP received, reloading configuration")
    server.expect(u"Loaded the config file")
    server.expect(updated_instance_address)
