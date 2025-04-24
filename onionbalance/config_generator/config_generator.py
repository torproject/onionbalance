import argparse
import logging
import shutil
import os
import sys
import getpass
import yaml

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from stem.descriptor.hidden_service import HiddenServiceDescriptorV3

import onionbalance
from onionbalance.common import log
from onionbalance.hs_v3 import tor_ed25519

# Simplify the logging output for the command line tool
logger = log.get_config_generator_logger()


class ConfigGenerator(object):
    def __init__(self, args, interactive):
        self.args = args
        self.interactive = interactive

        self.output_path = None

        # A dictionary that maps services to their keys and instances:
        # { <service_onion_address> : (<ed25519_key>, instances) , ... }
        self.services = {}

        self.num_instances = None
        self.tag = None
        self.torrc_port_line = None
        self.instances = None
        self.master_dir = None
        self.config_file_path = None
        self.master_key_path = None

        # If this is set, it means that we read our private key from a tor
        # instance and hence we should just copy the private key over instead
        # of recreating the file (so that the Tor private key semantics are
        # maintained (see self.is_priv_key_in_tor_format in service.py)
        self.v3_loaded_key_from_file = False

        # Gather information required to create config file!
        self.gather_information()

        # Create config file!
        self.generate_config()

    def try_make_dir(self, path):
        """
        Try to create a directory (including any parent directories)
        """
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

    def gather_information(self):
        # Check if output directory exists, if not try create it
        self.output_path = self.get_output_path()
        self.master_dir = self.output_path

        # Allow the creation of multiple services for v3
        n_services = self.get_num_services()

        # Gather information for each service
        for i, _ in enumerate(range(n_services), start=1):
            # Load or generate the master key
            master_key, master_onion_address = self.load_master_key(i)

            # Generate keys for each instance
            self.num_instances, self.tag = self.get_num_instances(i)

            instances = self.create_instances()
            self.services[master_onion_address] = (master_key, instances)

    def generate_config(self):
        # Write master key for each service
        for onion_address, (master_key, _) in self.services.items():
            self.write_master_key_to_disk(onion_address, master_key)

        # Create the onionbalance config file
        self.create_yaml_config_file()

        logger.info("Done! Successfully generated Onionbalance config.")
        logger.info("Now please edit '%s' with a text editor to add/remove/edit your backend instances.",
                    self.config_file_path)

    def get_output_path(self):
        """
        Get path to output directory and create if needed
        """
        output_path = None
        if self.interactive:
            output_path = input("Enter path to store generated config "
                                "[{}]: ".format(os.path.abspath(self.args.output)))
        output_path = output_path or self.args.output
        try:
            self.try_make_dir(output_path)
        except OSError:
            logger.exception("Problem encountered when trying to create the "
                             "output directory %s.", os.path.abspath(output_path))
            sys.exit(1)
        else:
            logger.debug("Created the output directory '%s'.",
                         os.path.abspath(output_path))

        config_path = os.path.join(output_path, 'config.yaml')
        if os.path.isfile(config_path):
            logger.error("The specified output directory '%s' already contains a 'config.yaml' "
                         "file. Please clean the directory before starting config_generator.",
                         output_path)
            sys.exit(1)

        return output_path

    def load_master_key(self, i):
        """
        Return the key and onion address of the frontend service.
        """
        self.master_key_path = self.get_master_key_path(i)

        # master_key_path is now either None (if no key path is specified) or
        # set to the actual path
        return self.load_v3_master_key(self.master_key_path)

    def get_master_key_path(self, i):
        # Load master key if specified
        master_key_path = None
        helper = " (i.e. path to 'hs_ed25519_secret_key')"
        if self.interactive:
            # Read key path from user
            master_key_path = input("Service #%d: Enter path to master service private key%s "
                                    "(Leave empty to generate a key): " %
                                    (i, helper))
        master_key_path = self.args.key or master_key_path

        # If a key path was specified make sure it exists
        if master_key_path:
            if not os.path.isfile(master_key_path):
                logger.error("The specified master service private key '%s' "
                             "could not be found. Please confirm the path and "
                             "file permissions are correct.", master_key_path)
                sys.exit(1)

        return master_key_path

    def _load_v3_master_key_from_file(self, master_key_path):
        """
        Load a private key straight from a Tor instance (no OBv3 keys supported)
        and return the private key and onion address.
        """
        try:
            with open(master_key_path, 'rb') as handle:
                pem_key_bytes = handle.read()
        except EnvironmentError as e:
            logger.error("Unable to read service private key file ('%s')", e)
            sys.exit(1)

        try:
            master_private_key = tor_ed25519.load_tor_key_from_disk(pem_key_bytes)
        except ValueError:
            logger.error("Please provide path to a valid Tor master key")
            sys.exit(1)
        identity_pub_key = master_private_key.public_key()
        identity_pub_key_bytes = identity_pub_key.public_bytes(encoding=serialization.Encoding.Raw,
                                                               format=serialization.PublicFormat.Raw)
        master_onion_address = HiddenServiceDescriptorV3.address_from_identity_key(identity_pub_key_bytes)

        # remove the trailing .onion
        master_onion_address = master_onion_address.replace(".onion", "")

        self.v3_loaded_key_from_file = True

        return master_private_key, master_onion_address

    def load_v3_master_key(self, master_key_path):
        if master_key_path: # load key from file
            # here we need to make many of these
            return self._load_v3_master_key_from_file(master_key_path)
        else: # generate new v3 key
            master_private_key = Ed25519PrivateKey.generate()
            master_public_key = master_private_key.public_key()
            master_pub_key_bytes = master_public_key.public_bytes(encoding=serialization.Encoding.Raw,
                                                                  format=serialization.PublicFormat.Raw)
            master_onion_address = HiddenServiceDescriptorV3.address_from_identity_key(master_pub_key_bytes)
            # cut out the onion since that's what the rest of the code expects
            master_onion_address = master_onion_address.replace(".onion", "")

            return master_private_key, master_onion_address

    def get_num_services(self):
        """
        Get the number of services this OnionBalance should support
        """
        num_services = None
        if self.interactive:
            num_services = input("Number of services (frontends) to create (default: %d): " %
                                 self.args.num_services)
            # Cast to int if a number was specified
            try:
                num_services = int(num_services)
            except ValueError:
                num_services = None

        num_services = num_services or self.args.num_services
        logger.debug("Creating %d services", num_services)
        return num_services

    def get_num_instances(self, i):
        """
        Get the number of instances and a tag name for them.
        """
        num_instances = None
        if self.interactive:
            limits = " (min: 1, max: 8)"
            num_instances = input("Service #%d: Number of instance services to create (default: %d)%s: " %
                                  (i, self.args.num_instances, limits))
            # Cast to int if a number was specified
            try:
                num_instances = int(num_instances)
            except ValueError:
                num_instances = None
        num_instances = num_instances or self.args.num_instances
        logger.debug("Creating %d service instances.", num_instances)

        tag = None
        if self.interactive:
            tag = input("Service #%d: Provide a tag name to group these instances [%s]:" %
                        (i, self.args.tag))
        tag = tag or self.args.tag

        return num_instances, tag

    def get_torrc_port_line(self):
        """
        Get the HiddenServicePort line for the instance torrc file
        """
        service_virtual_port = None
        if self.interactive:
            service_virtual_port = input("Specify the service virtual port (for "
                                         "client connections) [{}]: ".format(
                                             self.args.service_virtual_port))
        service_virtual_port = service_virtual_port or self.args.service_virtual_port

        service_target = None
        if self.interactive:
            # In interactive mode, change default target to match the specified
            # virtual port
            default_service_target = u'127.0.0.1:{}'.format(service_virtual_port)
            service_target = input("Specify the service target IP and port (where "
                                   "your service is listening) [{}]: ".format(
                                       default_service_target))
            service_target = service_target or default_service_target
        service_target = service_target or self.args.service_target
        torrc_port_line = u'HiddenServicePort {} {}'.format(service_virtual_port,
                                                            service_target)
        return torrc_port_line

    def create_instances(self):
        instances = []

        for i in range(0, self.num_instances):
            instances.append(("<Enter the instance onion address here>", None))

        return instances

    def get_master_key_passphrase(self):
        # Get optional passphrase for master key
        # [TODO: Implement for v3]
        master_passphrase = None
        if self.interactive:
            master_passphrase = getpass.getpass(
                "Provide an optional password to encrypt the master private "
                "key (Not encrypted if no password is specified): ")
        return master_passphrase or self.args.password

    def write_master_key_to_disk(self, onion_address, master_key):
        # Finished reading input, starting to write config files.
        self.try_make_dir(self.master_dir)
        master_key_file = os.path.join(self.master_dir,
                                       '{}.key'.format(onion_address))
        with open(master_key_file, "wb") as key_file:
            os.chmod(master_key_file, 384)  # chmod 0600 in decimal

            if self.v3_loaded_key_from_file:
                # If we loaded a v3 key from a file, copy the file directly
                # (see loaded_key_from_file comments).
                shutil.copyfile(self.master_key_path, master_key_file)
                logger.info("Copied v3 master key from %s to %s.",
                            self.master_key_path, master_key_file)
            else:
                # If we generated our own v3 master key, write it to file. If
                # 'master_key' does not exist, it means that we are loading it
                # from a file, so we dont need to write it to disk.
                master_key_formatted = master_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                                format=serialization.PrivateFormat.PKCS8,
                                                                encryption_algorithm=serialization.NoEncryption())
                key_file.write(master_key_formatted)

            logger.debug("Successfully wrote master key to file %s.",
                         os.path.abspath(master_key_file))

    def create_yaml_config_file(self):
        services_data = []

        # Create an entry for each service
        for onion_address, (_, instances) in self.services.items():
            # Create YAML Onionbalance settings file for these instances
            service_data = {'key': '{}.key'.format(onion_address)}
            service_data['instances'] = [{'address': address,
                                          'name': '{}{}'.format(self.tag, i + 1)} for
                                         i, (address, _) in enumerate(instances)]
            services_data.append(service_data)

        # Yamlify the config
        settings_data = {'services': services_data}
        config_yaml = yaml.safe_dump(settings_data, default_flow_style=False)

        self.config_file_path = os.path.join(self.master_dir, 'config.yaml')
        with open(self.config_file_path, "w") as config_file:
            config_file.write(u"# Onionbalance Config File\n")
            config_file.write(config_yaml)
            logger.info("Wrote master service config file '%s'.",
                        os.path.abspath(self.config_file_path))


def parse_cmd_args():
    """
    Parses and returns command line arguments for config generator
    """

    parser = argparse.ArgumentParser(
        prog="onionbalance-config",
        description="onionbalance-config generates config files and keys for "
        "Onionbalance instances and management servers. Calling without any "
        "options will initiate an interactive mode.")

    parser.add_argument("--hs-version", type=str,
                        default="v3", choices=("v3", ),
                        help="Onion service version (only v3 is supported).")

    parser.add_argument("--key", type=str, default=None,
                        help="RSA private key for the master onion service.")

    parser.add_argument("-p", "--password", type=str, default=None,
                        help="Optional password which can be used to encrypt "
                        "the master service private key.")

    parser.add_argument("-n", type=int, default=2, dest="num_instances",
                        help="Number of instances to generate (default: "
                        "%(default)s).")

    parser.add_argument("-s", type=int, default=1, dest="num_services",
                        help="Number of services to generate (default: "
                        "%(default)s).")

    parser.add_argument("-t", "--tag", type=str, default='node',
                        help="Prefix name for the service instances "
                        "(default: %(default)s).")

    parser.add_argument("--output", type=str, default='config/',
                        help="Directory to store generate config files. "
                        "The directory will be created if it does not "
                        "already exist (default: %(default)s).")

    parser.add_argument("--no-interactive", action='store_true',
                        help="Try to run automatically without prompting for "
                        "user input.")

    parser.add_argument("-v", type=str, default="info", dest='verbosity',
                        help="Minimum verbosity level for logging. Available "
                        "in ascending order: debug, info, warning, error, "
                        "critical) (default: %(default)s).")

    parser.add_argument("--service-virtual-port", type=str,
                        default="80",
                        help="Onion service port for external client "
                        "connections (default: %(default)s).")

    # TODO: Add validator to check if the target host:port line makes sense.
    parser.add_argument("--service-target", type=str,
                        default="127.0.0.1:80",
                        help="Target IP and port where your service is "
                        "listening (default: %(default)s).")

    # .. todo:: Add option to specify HS host and port for instance torrc

    parser.add_argument('--version', action='version',
                        version='onionbalance %s' % onionbalance.__version__)

    return parser


def main():
    """
    Entry point for interactive config file generation.
    """

    # Parse initial command line options
    args = parse_cmd_args().parse_args()

    logger.info("Beginning Onionbalance config generation.")

    # If CLI options have been provided, don't enter interactive mode
    # Crude check to see if any options beside --verbosity are set.
    verbose = True if '-v' in sys.argv else False

    if ((len(sys.argv) > 1 and not verbose) or len(sys.argv) > 3 or args.no_interactive):
        interactive = False
        logger.info("Entering non-interactive mode.")
    else:
        interactive = True
        logger.info("No command line arguments found, entering interactive "
                    "mode.")

    logger.setLevel(logging.__dict__[args.verbosity.upper()])

    # Start the config generator!
    try:
        ConfigGenerator(args, interactive)
    except KeyboardInterrupt:
        logger.warning("\nConfig generator got interrupted! There might be temporary configuration files left over... Bye!")

    sys.exit(0)
