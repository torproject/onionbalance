import datetime

import onionbalance.common.instance
from onionbalance.common import log

from onionbalance.hs_v3 import descriptor as ob_descriptor

logger = log.get_logger()


class InstanceV3(onionbalance.common.instance.Instance):
    """
    This is a V3 onionbalance instance
    """

    def __init__(self, onion_address):
        # Get the controller
        from onionbalance.hs_v3.onionbalance import my_onionbalance
        controller = my_onionbalance.controller.controller

        # Initialize the common Instance class.
        super().__init__(controller, onion_address)

        # Onion address does not contain the '.onion'.
        logger.warning("Loaded instance %s", onion_address)

        self.descriptor = None

        # When was the intro set of this instance last modified?
        self.intro_set_modified_timestamp = None

    def has_onion_address(self, onion_address):
        """
        Return True if this instance has this onion address
        """
        # Strip the ".onion" part of the address if it exists since some
        # subsystems don't use it (e.g. Tor sometimes omits it from control
        # port responses)
        my_onion_address = self.onion_address.replace(".onion", "")
        their_onion_address = onion_address.replace(".onion", "")

        return my_onion_address == their_onion_address

    def register_descriptor(self, descriptor_text, onion_address):
        """
        We received a descriptor (with 'descriptor_text') for 'onion_address'.
        Register it to this instance.
        """
        logger.info("Found instance %s for this new descriptor!", self.onion_address)

        assert(onion_address == self.onion_address)

        # Parse descriptor. If it parsed correctly, we know that this
        # descriptor is truly for this instance (since the onion address
        # matches)
        try:
            new_descriptor = ob_descriptor.ReceivedDescriptor(descriptor_text, onion_address)
        except ob_descriptor.BadDescriptor:
            logger.warning("Received bad descriptor for %s. Ignoring.", self.onion_address)
            return

        # Before replacing the current descriptor with this one, check if the
        # introduction point set changed:

        # If this is the first descriptor for this instance, the intro point set changed
        if not self.descriptor:
            logger.info("This is the first time we see a descriptor for instance %s!", self.onion_address)
            self.intro_set_modified_timestamp = datetime.datetime.utcnow()
            self.descriptor = new_descriptor
            return

        assert(self.descriptor)
        assert(new_descriptor.intro_set)

        # We already have a descriptor but this is a new one. Check the intro points!
        if new_descriptor.intro_set != self.descriptor.intro_set:
            logger.info("We got a new descriptor for instance %s and the intro set changed!", self.onion_address)
            self.intro_set_modified_timestamp = datetime.datetime.utcnow()
        else:
            logger.info("We got a new descriptor for instance %s but the intro set did not change.", self.onion_address)

        self.descriptor = new_descriptor

    def get_intros_for_publish(self):
        """
        Get a list of stem.descriptor.IntroductionPointV3 objects for this descriptor

        Raise :InstanceHasNoDescriptor: if there is no descriptor for this instance
        Raise :InstanceIsOffline: if the instance is offline.
        """
        if not self.descriptor:
            raise InstanceHasNoDescriptor

        if self.descriptor.is_old():
            raise InstanceIsOffline

        return self.descriptor.get_intro_points()


class InstanceHasNoDescriptor(Exception):
    pass


class InstanceIsOffline(Exception):
    pass
