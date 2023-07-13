# -*- coding: utf-8 -*-
import signal
import sys
import time

import pexpect

from test.functional.util import parse_chutney_environment, random_onionv3_address, create_test_config_file_v3

def test_sighup_reload_config(tmpdir, num_instances=30):
    """
    Functional test to run Onionbalance, send SIGHUP then check if config is reloaded
    """

    # run Chutney net and set Chutney environment manually - because reading from OS environment didn't work
    os.environ['CHUTNEY_ONION_ADDRESS'] = 'sd7wsgranoxlz6o3rhcxftez465cfvq6vdjkr3mqxriqpcmxo7ocdaad.onion:5858'
    os.environ['CHUTNEY_CLIENT_PORT'] = 'localhost:9008'

    chutney_config = parse_chutney_environment()

    list_instances = []
    i = 0
    while i < num_instances:
        list_instances.append(random_onionv3_address())
        i += 1

    config_file_path = create_test_config_file_v3(tmppath=tmpdir, instance_address=list_instances,
                                                  num_instances=num_instances)
    assert config_file_path

    # Start an Onionbalance server and monitor for correct output with pexpect
    server = pexpect.spawn("onionbalance",
                            args=[
                                '--hs-version', 'v3',
                                '-i', chutney_config.get('client_ip'),
                                '-p', str(chutney_config.get('control_port')),
                                '-c', config_file_path,
                                '-v', 'debug',
                                '--is-testnet'
                            ], logfile=sys.stdout.buffer, timeout=5)
    time.sleep(1)

    # Check for expected output from Onionbalance
    server.expect(u"Loaded the config file")
    server.expect(list_instances)

    # Update config file and send SIGHUP
    list_updated_instances = []
    i = 0
    while i < num_instances:
        list_updated_instances.append(random_onionv3_address())
        i += 1

    config_file_path = update_test_config_file_v3(tmppath=tmpdir, instance_address=list_updated_instances,
                                                  num_instances=num_instances)
    assert config_file_path
    server.kill(signal.SIGHUP)
    server.expect(u"Signal SIGHUP received, reloading configuration")
    server.expect(u"Loaded the config file")
    server.expect(list_updated_instances)
