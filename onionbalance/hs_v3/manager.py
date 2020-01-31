from setproctitle import setproctitle  # pylint: disable=no-name-in-module

import logging

from onionbalance import __version__

from onionbalance.common import scheduler
from onionbalance.common import log
from onionbalance.common import argparser
from onionbalance.common import signalhandler

from onionbalance.hs_v3 import params
from onionbalance.hs_v3 import onionbalance

logger = log.get_logger()

def main():
    logger.warning("Initializing onionbalance (version: %s)...", __version__)

    setproctitle('onionbalance')
    parser = argparser.get_common_argparser()

    parser.add_argument("--is-testnet", action='store_true',
                        help="Is this onionbalance on a test net? (Default: no)")

    args = parser.parse_args()

    # Override the log level if specified on the command line.
    if args.verbosity:
        params.DEFAULT_LOG_LEVEL = args.verbosity.upper()
    logger.setLevel(logging.__dict__[params.DEFAULT_LOG_LEVEL.upper()])

    # Get the global onionbalance singleton
    my_onionbalance = onionbalance.my_onionbalance
    my_onionbalance.init_subsystems(args)

    signalhandler.SignalHandler(my_onionbalance.controller.controller)

    # Schedule descriptor fetch and upload events
    if my_onionbalance.is_testnet:
        scheduler.add_job(params.FETCH_DESCRIPTOR_FREQUENCY_TESTNET, my_onionbalance.fetch_instance_descriptors)
        scheduler.add_job(params.PUBLISH_DESCRIPTOR_CHECK_FREQUENCY_TESTNET, my_onionbalance.publish_all_descriptors)
    else:
        scheduler.add_job(params.FETCH_DESCRIPTOR_FREQUENCY, my_onionbalance.fetch_instance_descriptors)
        scheduler.add_job(params.PUBLISH_DESCRIPTOR_CHECK_FREQUENCY, my_onionbalance.publish_all_descriptors)

    # Run initial fetch of HS instance descriptors
    scheduler.run_all(delay_seconds=params.INITIAL_CALLBACK_DELAY)

    # Begin main loop to poll for HS descriptors
    scheduler.run_forever()

    return 0

if __name__ == '__main__':
    main()

