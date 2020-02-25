import time

import stem.control

from onionbalance.common import log
import onionbalance.common.util

logger = log.get_logger()


def helper_fetch_all_instance_descriptors(controller, instances, control_password=None):
    """
    Try fetch fresh descriptors for all HS instances
    """
    logger.info("Initiating fetch of descriptors for all service instances.")

    # pylint: disable=no-member

    while True:
        try:
            # Clear Tor descriptor cache before making fetches by sending
            # the NEWNYM singal
            controller.signal(stem.control.Signal.NEWNYM)
            time.sleep(5)  # Sleep to allow Tor time to build new circuits
            pass
        except stem.SocketClosed:
            logger.error("Failed to send NEWNYM signal, socket is closed.")
            onionbalance.common.util.reauthenticate(controller, logger, control_password)
        else:
            break

    unique_instances = set(instances)

    # Only try to retrieve the descriptor once for each unique instance
    # address. An instance may be configured under multiple master
    # addressed. We do not want to request the same instance descriptor
    # multiple times.
    # OnionBalance will update all of the matching instances when a
    # descriptor is received.
    for instance in unique_instances:
        while True:
            try:
                instance.fetch_descriptor()
            except stem.SocketClosed:
                logger.error("Failed to fetch descriptor, socket is closed")
                onionbalance.common.util.reauthenticate(controller, logger, control_password)
            else:
                break


class Instance(object):
    """
    Instance represents a back-end load balancing hidden service.
    """

    def __init__(self, controller, onion_address, authentication_cookie=None):
        """
        Initialise an Instance object.
        """
        self.controller = controller

        # Onion address for the service instance.
        if onion_address:
            onion_address = onion_address.replace('.onion', '')
        self.onion_address = onion_address

        # Flag this instance with its introduction points change. A new
        # master descriptor will then be published as the introduction
        # points have changed.
        self.intro_set_changed_since_published = False

    def fetch_descriptor(self):
        """
        Try fetch a fresh descriptor for this service instance from the HSDirs
        """
        logger.debug("Trying to fetch a descriptor for instance %s.onion.",
                     self.onion_address)
        try:
            self.controller.get_hidden_service_descriptor(self.onion_address,
                                                          await_result=False)
        except stem.SocketClosed:
            # Tor maybe restarting.
            raise
        except stem.DescriptorUnavailable:
            # Could not find the descriptor on the HSDir
            self.received = None
            logger.warning("No descriptor received for instance %s.onion, "
                           "the instance may be offline.", self.onion_address)

    def __eq__(self, other):
        """
        Instance objects are equal if they have the same onion address.
        """
        if isinstance(other, Instance):
            return self.onion_address == other.onion_address
        else:
            return False

    def __hash__(self):
        """
        Define __hash__ method allowing for set comparison between instances.
        """
        return hash(self.onion_address)
