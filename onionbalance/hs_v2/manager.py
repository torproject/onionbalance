# -*- coding: utf-8 -*-
"""
Load balance a hidden service across multiple (remote) Tor instances by
create a hidden service descriptor containing introduction points from
each instance.
"""
import sys
import logging

# import Cryptodome.PublicKey
import stem
from stem.control import EventType

import onionbalance.common.util

from onionbalance.common import scheduler
from onionbalance.common import log
from onionbalance.common import signalhandler

from onionbalance.hs_v2 import config
from onionbalance.hs_v2 import eventhandler
from onionbalance.hs_v2 import settings
from onionbalance.hs_v2 import status

from onionbalance.hs_v2.service import publish_all_descriptors
from onionbalance.hs_v2.instance import fetch_instance_descriptors

logger = log.get_logger()


def main(args):
    """
    Entry point when invoked over the command line.
    """
    config_file_options = settings.parse_config_file(args.config)

    # Update global configuration with options specified in the config file
    for setting in dir(config):
        if setting.isupper() and config_file_options.get(setting):
            setattr(config, setting, config_file_options.get(setting))

    # Override the log level if specified on the command line.
    if args.verbosity:
        config.LOG_LEVEL = args.verbosity.upper()

    # Write log file if configured in environment variable or config file
    if config.LOG_LOCATION:
        log.setup_file_logger(config.LOG_LOCATION)

    logger.setLevel(logging.__dict__[config.LOG_LEVEL.upper()])

    controller = onionbalance.common.util.connect_to_control_port(args.socket, args.ip, args.port,
                                                                  config.TOR_CONTROL_PASSWORD)

    status_socket = status.StatusSocket(config.STATUS_SOCKET_LOCATION)
    signalhandler.SignalHandler('v2', controller, status_socket)

    # Disable no-member due to bug with "Instance of 'Enum' has no * member"
    # pylint: disable=no-member

    # Check that the Tor client supports the HSPOST control port command
    if not controller.get_version() >= stem.version.Requirement.HSPOST:
        logger.error("A Tor version >= %s is required. You may need to "
                     "compile Tor from source or install a package from "
                     "the experimental Tor repository.",
                     stem.version.Requirement.HSPOST)
        sys.exit(1)

    # Load the keys and config for each onion service
    settings.initialize_services(controller,
                                 config_file_options.get('services'))

    # Finished parsing all the config file.

    handler = eventhandler.EventHandler()
    controller.add_event_listener(handler.new_status,
                                  EventType.STATUS_CLIENT)
    controller.add_event_listener(handler.new_desc,
                                  EventType.HS_DESC)
    controller.add_event_listener(handler.new_desc_content,
                                  EventType.HS_DESC_CONTENT)

    # Schedule descriptor fetch and upload events
    scheduler.add_job(config.REFRESH_INTERVAL, fetch_instance_descriptors,
                      controller)
    scheduler.add_job(config.PUBLISH_CHECK_INTERVAL, publish_all_descriptors)

    # Run initial fetch of HS instance descriptors
    scheduler.run_all(delay_seconds=config.INITIAL_DELAY)

    # Begin main loop to poll for HS descriptors
    scheduler.run_forever()

    return 0
