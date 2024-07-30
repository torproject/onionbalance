# -*- coding: utf-8 -*-
import base64
import os
import socket

import Cryptodome.PublicKey.RSA
import pytest
import yaml
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat

from onionbalance.config_generator.config_generator import ConfigGenerator, parse_cmd_args

# Skip functional tests if Chutney environment is not running.
pytestmark = pytest.mark.skipif(
    "os.environ.get('CHUTNEY_ONION_ADDRESS') is None",
    reason="Skipping functional test, no Chutney environment detected")


def parse_chutney_enviroment():
    """
    Read environment variables and determine chutney instance and
    client addresses.
    """

    tor_client = os.environ.get('CHUTNEY_CLIENT_PORT')
    assert tor_client

    # Calculate the address and port of clients control port
    client_address, client_socks_port = tor_client.split(':')
    client_ip = socket.gethostbyname(client_address)

    tor_client_number = int(client_socks_port) - 9000
    # Control port in the 8000-8999 range, offset by Tor client number
    control_port = 8000 + tor_client_number
    assert control_port

    # Retrieve instance onion address exported during chutney setup
    instance_address = os.environ.get('CHUTNEY_ONION_ADDRESS')
    assert instance_address  # Need at least 1 instance address for test

    return {
        'client_ip': client_ip,
        'control_port': control_port,
        'instances': [instance_address],
    }


def create_test_config_file_v2(tmppath, private_key=None, instances=None):
    """
    Setup function to create a temp directory with master key and config file.
    Returns a path to the temporary config file.

    .. todo:: Refactor settings.py config creation to avoid code duplication
              in integration tests.
    """

    if not private_key:
        private_key = Cryptodome.PublicKey.RSA.generate(1024)

    # Write private key file
    key_path = tmppath.join('private_key')
    key_path.write(private_key.exportKey())
    assert key_path.check()

    # Create YAML Onionbalance settings file for these instances
    service_data = {'key': str(key_path)}
    service_data['instances'] = [{'address': addr[:16]} for addr in instances]
    settings_data = {
        'services': [service_data],
        'STATUS_SOCKET_LOCATION': str(tmppath.join('control')),
    }
    config_yaml = yaml.dump(settings_data, default_flow_style=False)

    config_path = tmppath.join('config.yaml')
    config_path.write_binary(config_yaml.encode('utf-8'))
    assert config_path.check()

    return str(config_path)


def create_test_config_file_v3(tmppath, instance_address):
    args = parse_cmd_args().parse_args(['-n', '1', '--output', str(tmppath)])
    ConfigGenerator(args, False)

    config_path = tmppath.join('config.yaml')
    assert config_path.check()

    with open(config_path) as f:
        config = yaml.safe_load(f)
    config['services'][0]['instances'][0]['address'] = instance_address

    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return str(config_path)

def update_test_config_file_v3(tmppath, instance_address):
    config_path = tmppath.join('config.yaml')
    assert config_path.check()

    with open(config_path) as f:
        config = yaml.safe_load(f)
    config['services'][0]['instances'][0]['address'] = instance_address

    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return str(config_path)

def random_onionv3_address():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)

    # checksum = H(".onion checksum" || pubkey || version)
    checksumBytes = b''.join([b'.onion checksum', public_bytes, bytes([0x03])])
    digest = hashes.Hash(hashes.SHA3_256(), backend=default_backend())
    digest.update(checksumBytes)
    checksum = digest.finalize()[:2]

    # onion_address = base32(pubkey || checksum || version)
    onionAddressBytes = b''.join([public_bytes, checksum, bytes([0x03])])
    print(onionAddressBytes)
    onionAddress = base64.b32encode(onionAddressBytes).lower().decode('utf-8')

    return onionAddress + '.onion'
