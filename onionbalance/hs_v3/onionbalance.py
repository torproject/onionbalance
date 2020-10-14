import os
import sys

import stem
from stem.descriptor.hidden_service import HiddenServiceDescriptorV3

import onionbalance.common.instance

from onionbalance.common import log

from onionbalance.common import util
from onionbalance.hs_v3 import manager

from onionbalance.hs_v3 import stem_controller
from onionbalance.hs_v3 import service as ob_service
from onionbalance.hs_v3 import consensus as ob_consensus

logger = log.get_logger()


class Onionbalance(object):
    """
    Onionbalance singleton that represents this onionbalance runtime.

    Contains various objects that are useful to other onionbalance modules so
    this is imported from all over the codebase.
    """

    def __init__(self):
        # This is kept minimal so that it's quick (it's executed at program
        # launch because of the onionbalance singleton). The actual init work
        # happens in init_subsystems()

        # True if this onionbalance operates in a testnet (e.g. chutney)
        self.is_testnet = False

    def init_subsystems(self, args):
        """
        Initialize subsystems (this is resource intensive)
        """
        self.args = args
        self.config_path = os.path.abspath(self.args.config)
        self.config_data = self.load_config_file()
        self.is_testnet = args.is_testnet

        if self.is_testnet:
            logger.warning("Onionbalance configured on a testnet!")

        # Create stem controller and connect to the Tor network
        self.controller = stem_controller.StemController(address=args.ip, port=args.port, socket=args.socket)
        self.consensus = ob_consensus.Consensus()

        # Initialize our service
        self.services = self.initialize_services_from_config_data()

        # Catch interesting events (like receiving descriptors etc.)
        self.controller.add_event_listeners()

        logger.warning("Onionbalance initialized (stem version: %s) (tor version: %s)!",
                       stem.__version__, self.controller.controller.get_version())
        logger.warning("=" * 80)

    def initialize_services_from_config_data(self):
        services = []
        try:
            for service in self.config_data['services']:
                services.append(ob_service.OnionBalanceService(service, self.config_path))
        except ob_service.BadServiceInit:
            sys.exit(1)

        if len(services) > 1:
            # We don't know how to handle more than a single service right now
            raise NotImplementedError

        return services

    def load_config_file(self):
        config_data = util.read_config_data_from_file(self.config_path)
        logger.debug("Onionbalance config data: %s", config_data)

        # Do some basic validation
        if "services" not in config_data:
            raise ConfigError("Config file is bad. 'services' is missing. Did you make it with onionbalance-config?")

        # More validation
        for service in config_data["services"]:
            if "key" not in service:
                raise ConfigError("Config file is bad. 'key' is missing. Did you make it with onionbalance-config?")

            if "instances" not in service:
                raise ConfigError("Config file is bad. 'instances' is missing. Did you make it with "
                                  "onionbalance-config?")

            if not service["instances"]:
                raise ConfigError("Config file is bad. No backend instances are set. Onionbalance needs at least 1.")

            for instance in service["instances"]:
                if "address" not in instance:
                    raise ConfigError("Config file is wrong. 'address' missing from instance.")

                if not instance["address"]:
                    raise ConfigError("Config file is bad. Address field is not set.")

                # Validate that the onion address is legit
                try:
                    _ = HiddenServiceDescriptorV3.identity_key_from_address(instance["address"])
                except ValueError:
                    raise ConfigError("Cannot load instance with address: '{}'. If you are trying to run onionbalance "
                                      "for v2 onions, please use the --hs-version=v2 switch".format(instance["address"]))

        return config_data

    def fetch_instance_descriptors(self):
        logger.info("[*] fetch_instance_descriptors() called [*]")

        # TODO: Don't do this here. Instead do it on a specialized function
        self.controller.mark_tor_as_active()

        if not self.consensus.is_live():
            logger.warning("No live consensus. Waiting before fetching descriptors...")
            return

        all_instances = self._get_all_instances()

        onionbalance.common.instance.helper_fetch_all_instance_descriptors(self.controller.controller,
                                                                           all_instances)

    def handle_new_desc_content_event(self, desc_content_event):
        """
        Parse HS_DESC_CONTENT response events for descriptor content

        Update the HS instance object with the data from the new descriptor.
        """
        onion_address = desc_content_event.address
        logger.debug("Received descriptor for %s.onion from %s",
                     onion_address, desc_content_event.directory)

        #  Check that the HSDir returned a descriptor that is not empty
        descriptor_text = str(desc_content_event.descriptor).encode('utf-8')

        # HSDirs provide a HS_DESC_CONTENT response with either one or two
        # CRLF lines when they do not have a matching descriptor. Using
        # len() < 5 should ensure all empty HS_DESC_CONTENT events are matched.
        if len(descriptor_text) < 5:
            logger.debug("Empty descriptor received for %s.onion", onion_address)
            return None

        # OK this descriptor seems plausible: Find the instances that this
        # descriptor belongs to:
        for instance in self._get_all_instances():
            if instance.onion_address == onion_address:
                instance.register_descriptor(descriptor_text, onion_address)

    def publish_all_descriptors(self):
        """
        For each service attempt to publish all descriptors
        """
        logger.info("[*] publish_all_descriptors() called [*]")

        if not self.consensus.is_live():
            logger.info("No live consensus. Waiting before publishing descriptors...")
            return

        for service in self.services:
            service.publish_descriptors()

    def _get_all_instances(self):
        """
        Get all instances for all services
        """
        instances = []

        for service in self.services:
            instances.extend(service.instances)

        return instances

    def handle_new_status_event(self, status_event):
        """
        Parse Tor status events such as "STATUS_GENERAL"
        """
        # pylint: disable=no-member
        if status_event.action == "CONSENSUS_ARRIVED":
            logger.info("Received new consensus!")
            self.consensus.refresh()
            # Call all callbacks in case we just got a live consensus
            my_onionbalance.publish_all_descriptors()
            my_onionbalance.fetch_instance_descriptors()

    def _address_is_instance(self, onion_address):
        """
        Return True if 'onion_address' is one of our instances.
        """
        for service in self.services:
            for instance in service.instances:
                if instance.has_onion_address(onion_address):
                    return True
        return False

    def _address_is_frontend(self, onion_address):
        for service in self.services:
            if service.has_onion_address(onion_address):
                return True
        return False

    def handle_new_desc_event(self, desc_event):
        """
        Parse HS_DESC response events
        """
        action = desc_event.action

        if action == "RECEIVED":
            pass  # We already log in HS_DESC_CONTENT so no need to do it here too
        elif action == "UPLOADED":
            logger.debug("Successfully uploaded descriptor for %s to %s", desc_event.address, desc_event.directory)
        elif action == "FAILED":
            if self._address_is_instance(desc_event.address):
                logger.info("Descriptor fetch failed for instance %s from %s (%s)",
                            desc_event.address, desc_event.directory, desc_event.reason)
            elif self._address_is_frontend(desc_event.address):
                logger.warning("Descriptor upload failed for frontend %s to %s (%s)",
                               desc_event.address, desc_event.directory, desc_event.reason)
            else:
                logger.warning("Descriptor action failed for unknown service %s to %s (%s)",
                               desc_event.address, desc_event.directory, desc_event.reason)
        elif action == "REQUESTED":
            logger.debug("Requested descriptor for %s from %s...", desc_event.address, desc_event.directory)
        else:
            pass

    def reload_config(self):
        """
        Reload configuration and reset job scheduler
        """

        try:
            self.init_subsystems(self.args)
            manager.init_scheduler(self)
        except ConfigError as err:
            logger.error("%s", err)
            sys.exit(1)


class ConfigError(Exception):
    pass


my_onionbalance = Onionbalance()
