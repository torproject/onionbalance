# -*- coding: utf-8 -*-
import datetime

from onionbalance.common import log
from onionbalance.hs_v2 import config
import onionbalance.common.instance

logger = log.get_logger()


def fetch_instance_descriptors(controller):
    all_instances = [instance for service in config.services for instance in service.instances]

    onionbalance.common.instance.helper_fetch_all_instance_descriptors(controller, all_instances,
                                                                       control_password=config.TOR_CONTROL_PASSWORD)


class InstanceV2(onionbalance.common.instance.Instance):
    """
    This is a V2 onionbalance instance
    """

    def __init__(self, controller, onion_address, authentication_cookie):
        """
        Constructor for V2 instance
        """
        # Initialize the common instance class
        super().__init__(controller, onion_address)

        self.authentication_cookie = authentication_cookie

        # Store the latest set of introduction points for this instance
        self.introduction_points = []

        # Timestamp when last received a descriptor for this instance
        self.received = None

        # Timestamp of the currently loaded descriptor
        self.timestamp = None

    def update_descriptor(self, parsed_descriptor):
        """
        Update introduction points when a new HS descriptor is received

        Parse the descriptor content and update the set of introduction
        points for this HS instance. Returns True if the introduction
        point set has changed, False otherwise.`
        """

        self.received = datetime.datetime.utcnow()

        logger.debug("Received a descriptor for instance %s.onion.",
                     self.onion_address)

        # Reject descriptor if its timestamp is older than the current
        # descriptor. Prevents HSDirs from replaying old, expired
        # descriptors.
        if self.timestamp and parsed_descriptor.published < self.timestamp:
            logger.error("Received descriptor for instance %s.onion with "
                         "publication timestamp (%s) older than the latest "
                         "descriptor (%s). Ignoring the descriptor.",
                         self.onion_address,
                         parsed_descriptor.published,
                         self.timestamp)
            return False
        else:
            self.timestamp = parsed_descriptor.published

        # Parse the introduction point list, decrypting if necessary
        introduction_points = parsed_descriptor.introduction_points(
            authentication_cookie=self.authentication_cookie
        )

        # If the new introduction points are different, flag this instance
        # as modified. Compare the set of introduction point identifiers
        # (fingerprint of the per IP circuit service key).
        if (set(ip.identifier for ip in introduction_points) != set(ip.identifier for ip in self.introduction_points)):
            self.intro_set_changed_since_published = True
            self.introduction_points = introduction_points
            return True

        else:
            logger.debug("Introduction points for instance %s.onion matched "
                         "the cached set.", self.onion_address)
            return False
