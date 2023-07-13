# -*- coding: utf-8 -*-
import socket
import sys
import time

import Cryptodome.PublicKey.RSA
import pexpect
import stem.control

import onionbalance.hs_v2.util
from test.functional.util import *


def test_master_descriptor_publication(tmpdir):
    """
    Functional test to run Onionbalance, publish a master descriptor and
    check that it can be retrieved from the DHT.
    """

    chutney_config = parse_chutney_environment()
    print(chutney_config)
    private_key = Cryptodome.PublicKey.RSA.generate(1024)
    master_onion_address = onionbalance.hs_v2.util.calc_onion_address(private_key)

    config_file_path = create_test_config_file_v2(
        tmppath=tmpdir,
        private_key=private_key,
        instances=chutney_config.get('instances', []),
    )
    assert config_file_path

    # Start an Onionbalance server and monitor for correct output with pexpect
    server = pexpect.spawnu("onionbalance",
                            args=[
                                '--hs-version', 'v2',
                                '-i', chutney_config.get('client_ip'),
                                '-p', str(chutney_config.get('control_port')),
                                '-c', config_file_path,
                                '-v', 'debug',
                                '--is-testnet'
                            ], logfile=sys.stdout, timeout=15)

    # Check for expected output from Onionbalance
    server.expect(u"Loaded the config file")
    server.expect(u"introduction point set has changed")
    server.expect(u"Published a descriptor", timeout=60)

    # Check Tor control port gave an uploaded event.

    server.expect(u"HS_DESC UPLOADED")
    # Eek, sleep to wait for descriptor upload to all replicas to finish
    time.sleep(10)

    # .. todo:: Also need to check and raise for any warnings or errors
    #           that are emitted

    # Try fetch and validate the descriptor with stem
    with stem.control.Controller.from_port(
        address=chutney_config.get('client_ip'),
        port=chutney_config.get('control_port')
    ) as controller:
        controller.authenticate()

        # get_hidden_service_descriptor() will raise exceptions if it
        # cannot find the descriptors
        master_descriptor = controller.get_hidden_service_descriptor(
            master_onion_address)
        master_ips = master_descriptor.introduction_points()

        # Try retrieve a descriptor for each instance
        for instance_address in chutney_config.get('instances'):
            instance_descriptor = controller.get_hidden_service_descriptor(
                instance_address.split(':')[0])
            instance_ips = instance_descriptor.introduction_points()

            # Check if all instance IPs were included in the master descriptor
            assert (set(ip.identifier for ip in instance_ips) ==
                    set(ip.identifier for ip in master_ips))

    # Check that the control socket was created
    socket_path = tmpdir.join('control')
    assert socket_path.check()

    # Connect to the control socket and check the output
    sock_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock_client.connect(str(socket_path))

    # Read the data from the status socket
    result = []
    while True:
        data = sock_client.recv(1024)
        if not data:
            break
        result.append(data.decode('utf-8'))
    result_data = ''.join(result)

    # Check each instance is in the output
    for instance_address in chutney_config.get('instances'):
        assert instance_address.split(':')[0] in result_data

    # Check all instances were online and all master descriptors uploaded
    assert master_onion_address in result_data
    assert '[offline]' not in result_data
    assert '[not uploaded]' not in result_data

