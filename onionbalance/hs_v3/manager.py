import logging

from onionbalance.common import scheduler
from onionbalance.common import log
from onionbalance.common import signalhandler

from onionbalance.hs_v3 import params
from onionbalance.hs_v3 import onionbalance

logger = log.get_logger()


def main(args):
    """
    This is the entry point of v3 functionality.

    Initialize onionbalance, schedule future jobs and let the scheduler do its thing.
    """

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
