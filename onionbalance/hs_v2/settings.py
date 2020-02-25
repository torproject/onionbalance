# -*- coding: utf-8 -*-

"""
Implements the generation and loading of configuration files.
"""
import os
import sys
import errno

from onionbalance.hs_v2 import config
from onionbalance.common import log

import onionbalance.hs_v2.util
import onionbalance.common.util

import onionbalance.hs_v2.service
import onionbalance.hs_v2.instance

logger = log.get_logger()


def parse_config_file(config_file):
    """
    Parse config file containing service information
    """
    config_path = os.path.abspath(config_file)
    config_data = onionbalance.common.util.read_config_data_from_file(config_path)

    # Rewrite relative paths in the config to be relative to the config
    # file directory
    config_directory = os.path.dirname(config_path)
    for service in config_data.get('services'):
        if not os.path.isabs(service.get('key')):
            service['key'] = os.path.join(config_directory, service['key'])

    return config_data


def initialize_services(controller, services_config):
    """
    Load keys for services listed in the config
    """

    # Load the keys and config for each onion service
    for service in services_config:
        try:
            service_key = onionbalance.hs_v2.util.key_decrypt_prompt(service.get("key"))
        except ValueError as e:
            logger.error("Got exception '%s'. Perhaps you are trying to load a v3 onion service "
                         "but with --hs-version=v2 enabled?", e)
            sys.exit(1)
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                logger.error("Private key file %s could not be found. "
                             "Relative paths in the config file are loaded "
                             "relative to the config file directory.",
                             service.get("key"))
                sys.exit(1)
            elif e.errno == errno.EACCES:
                logger.error("Permission denied to private key %s.",
                             service.get("key"))
                sys.exit(1)
            else:
                raise
        # Key file was read but a valid private key was not found.
        if not service_key:
            logger.error("Private key %s could not be loaded. It is a not "
                         "valid 1024 bit PEM encoded RSA private key",
                         service.get("key"))
            sys.exit(1)
        else:
            # Successfully imported the private key
            onion_address = onionbalance.hs_v2.util.calc_onion_address(service_key)
            logger.debug("Loaded private key for service %s.onion.",
                         onion_address)

        # Load all instances for the current onion service
        instance_config = service.get("instances", [])
        if not instance_config:
            logger.error("Could not load any instances for service "
                         "%s.onion.", onion_address)
            sys.exit(1)
        else:
            instances = []
            for instance in instance_config:
                instances.append(onionbalance.hs_v2.instance.InstanceV2(
                    controller=controller,
                    onion_address=instance.get("address"),
                    authentication_cookie=instance.get("auth")
                ))

            logger.info("Loaded %d instances for service %s.onion.",
                        len(instances), onion_address)

        # Store service configuration in config.services global
        config.services.append(onionbalance.hs_v2.service.Service(
            controller=controller,
            service_key=service_key,
            instances=instances
        ))

        # Store a global reference to current controller connection
        config.controller = controller
