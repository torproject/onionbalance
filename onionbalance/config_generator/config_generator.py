import argparse
import logging
import shutil
import os
import sys
import getpass
import yaml
import pkg_resources

import Cryptodome.PublicKey.RSA
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from stem.descriptor.hidden_service import HiddenServiceDescriptorV3

import onionbalance
from onionbalance.common import log
from onionbalance.hs_v2 import util
from onionbalance.hs_v3 import tor_ed25519

# Simplify the logging output for the command line tool
logger = log.get_config_generator_logger()


class ConfigGenerator(object):
    def __init__(self, args, interactive):
        self.args = args
        self.interactive = interactive

        self.hs_version = None
        self.output_path = None
        self.master_key = None
        self.master_onion_address = None
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

    def gather_information(self):
        self.hs_version = self.get_hs_version()
        assert(self.hs_version in ['v2', 'v3'])

        # Check if output directory exists, if not try create it
        self.output_path = self.get_output_path()

        if self.hs_version == "v2":
            self.master_dir = os.path.join(self.output_path, 'master')
        else:
            self.master_dir = self.output_path

        # Load the master key
        self.master_key, self.master_onion_address = self.load_master_key()

        # Finished loading/generating master key, now try generate keys for
        # each service instance
        self.num_instances, self.tag = self.get_num_instances()

        # Create HiddenServicePort line for instance torrc file
        if self.hs_version == 'v2':
            self.torrc_port_line = self.get_torrc_port_line()

        self.instances = self.create_instances()

    def generate_config(self):
        self.write_master_key_to_disk()

        assert(self.instances)

        # Create the onionbalance config file
        self.create_yaml_config_file()

        if self.hs_version == 'v2':
            # Generate config files for each service instance
            self.write_v2_instance_files()

            logger.info("Done! Successfully generated an OnionBalance config and %d "
                        "instance keys for service %s.onion.",
                        self.num_instances, self.master_onion_address)

        if self.hs_version == "v3":
            logger.info("Done! Successfully generated an OnionBalance config for service %s.onion.",
                        self.master_onion_address)
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
            util.try_make_dir(output_path)
        except OSError:
            logger.exception("Problem encountered when trying to create the "
                             "output directory %s.", os.path.abspath(output_path))
            sys.exit(1)
        else:
            logger.debug("Created the output directory '%s'.",
                         os.path.abspath(output_path))

        # Do some directory validation
        if self.hs_version == 'v2' and not util.is_directory_empty(output_path):
            # The output directory should be empty to avoid having conflict keys
            # or config files.
            logger.error("The specified output directory '%s' is not empty. Please "
                         "delete any files and folders or specify another output "
                         "directory.", output_path)
            sys.exit(1)
        elif self.hs_version == 'v3':
            config_path = os.path.join(output_path, 'config.yaml')
            if os.path.isfile(config_path):
                logger.error("The specified output directory '%s' already contains a 'config.yaml' "
                             "file. Please clean the directory before starting config_generator.",
                             output_path)
                sys.exit(1)

        return output_path

    def get_hs_version(self):
        # Get the HS version
        hs_version = None
        if self.interactive:
            hs_version = input('Enter HS version ("v2" or "v3") (Leave empty for "v3"): ')
        hs_version = hs_version or self.args.hs_version

        if hs_version not in ["v2", "v3"]:
            logger.error('Only accepting "v2" and "v3" as HS versions')
            sys.exit(1)

        logger.info("Rolling with HS %s!", hs_version)

        return hs_version

    def load_master_key(self):
        """
        Return the key and onion address of the frontend service.
        """
        self.master_key_path = self.get_master_key_path()

        # master_key_path is now either None (if no key path is specified) or
        # set to the actual path
        if self.hs_version == 'v2':
            return self.load_v2_master_key(self.master_key_path)
        else:
            return self.load_v3_master_key(self.master_key_path)

    def get_master_key_path(self):
        # Load master key if specified
        master_key_path = None
        helper = " (i.e. path to 'hs_ed25519_secret_key')" if self.hs_version == 'v3' else ""
        if self.interactive:
            # Read key path from user
            master_key_path = input("Enter path to master service private key%s "
                                    "(Leave empty to generate a key): " % (helper))
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

    def load_v2_master_key(self, master_key_path):
        if master_key_path:
            # Try load the specified private key file
            master_key = util.key_decrypt_prompt(master_key_path)
            if not master_key:
                logger.error("The specified master private key %s could not "
                             "be loaded.", os.path.abspath(master_key))
                sys.exit(1)

            master_onion_address = util.calc_onion_address(master_key)
            logger.info("Successfully loaded a master key for service "
                        "%s.onion.", master_onion_address)
        else:
            # No key specified, begin generating a new one.
            master_key = Cryptodome.PublicKey.RSA.generate(1024)
            master_onion_address = util.calc_onion_address(master_key)
            logger.debug("Created a new master key for service %s.onion.",
                         master_onion_address)

        return master_key, master_onion_address

    def get_num_instances(self):
        """
        Get the number of instances and a tag name for them.
        """
        num_instances = None
        if self.interactive:
            limits = " (min: 1, max: 8)" if self.hs_version == "v3" else ""
            num_instances = input("Number of instance services to create (default: %d)%s: " %
                                  (self.args.num_instances, limits))
            # Cast to int if a number was specified
            try:
                num_instances = int(num_instances)
            except ValueError:
                num_instances = None
        num_instances = num_instances or self.args.num_instances
        logger.debug("Creating %d service instances.", num_instances)

        tag = None
        if self.interactive:
            tag = input("Provide a tag name to group these instances "
                        "[{}]: ".format(self.args.tag))
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
        if self.hs_version == 'v2':
            return self.create_v2_instances()
        else:
            return self.create_v3_instances()

    def create_v2_instances(self):
        instances = []

        for i in range(0, self.num_instances):
            instance_key = Cryptodome.PublicKey.RSA.generate(1024)
            instance_address = util.calc_onion_address(instance_key)
            logger.debug("Created a key for instance %s.onion.",
                         instance_address)
            instances.append((instance_address, instance_key))

        return instances

    def create_v3_instances(self):
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

    def write_master_key_to_disk(self):
        # Finished reading input, starting to write config files.
        util.try_make_dir(self.master_dir)
        master_key_file = os.path.join(self.master_dir,
                                       '{}.key'.format(self.master_onion_address))
        with open(master_key_file, "wb") as key_file:
            os.chmod(master_key_file, 384)  # chmod 0600 in decimal

            if self.hs_version == 'v2':
                master_passphrase = self.get_master_key_passphrase()
                key_file.write(self.master_key.exportKey(passphrase=master_passphrase))
            elif self.hs_version == 'v3' and self.v3_loaded_key_from_file:
                # If we loaded a v3 key from a file, copy the file directly
                # (see loaded_key_from_file comments).
                shutil.copyfile(self.master_key_path, master_key_file)
                logger.info("Copied v3 master key from %s to %s.",
                            self.master_key_path, master_key_file)
            else:
                # If we generated our own v3 master key, write it to file. If
                # 'master_key' does not exist, it means that we are loading it
                # from a file, so we dont need to write it to disk.
                master_key_formatted = self.master_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                                     format=serialization.PrivateFormat.PKCS8,
                                                                     encryption_algorithm=serialization.NoEncryption())
                key_file.write(master_key_formatted)

            logger.debug("Successfully wrote master key to file %s.",
                         os.path.abspath(master_key_file))

    def write_v2_instance_files(self):
        for i, (instance_address, instance_key) in enumerate(self.instances):
            # Create a numbered directory for instance
            instance_dir = os.path.join(self.output_path, '{}{}'.format(self.tag, i + 1))
            instance_key_dir = os.path.join(instance_dir, instance_address)
            util.try_make_dir(instance_key_dir)
            os.chmod(instance_key_dir, 1472)  # chmod 2700 in decimal

            instance_key_file = os.path.join(instance_key_dir, 'private_key')
            with open(instance_key_file, "wb") as key_file:
                os.chmod(instance_key_file, 384)  # chmod 0600 in decimal
                key_file.write(instance_key.exportKey())
                logger.debug("Successfully wrote key for instance %s.onion to "
                             "file.", instance_address)

            # Write torrc file for each instance
            instance_torrc = os.path.join(instance_dir, 'instance_torrc')
            instance_torrc_template = pkg_resources.resource_string(
                __name__, 'data/torrc-instance-v2')
            with open(instance_torrc, "w") as torrc_file:
                torrc_file.write(instance_torrc_template.decode('utf-8'))
                # The ./ relative path prevents Tor from raising relative
                # path warnings. The relative path may need to be edited manual
                # to work on Windows systems.
                torrc_file.write(u"HiddenServiceDir {}\n".format(
                    instance_address))
                torrc_file.write(u"{}\n".format(self.torrc_port_line))

    def create_yaml_config_file(self):
        # Create YAML OnionBalance settings file for these instances
        service_data = {'key': '{}.key'.format(self.master_onion_address)}
        service_data['instances'] = [{'address': address,
                                      'name': '{}{}'.format(self.tag, i + 1)} for
                                     i, (address, _) in enumerate(self.instances)]
        settings_data = {'services': [service_data]}
        config_yaml = yaml.safe_dump(settings_data, default_flow_style=False)

        self.config_file_path = os.path.join(self.master_dir, 'config.yaml')
        with open(self.config_file_path, "w") as config_file:
            config_file.write(u"# OnionBalance Config File\n")
            config_file.write(config_yaml)
            logger.info("Wrote master service config file '%s'.",
                        os.path.abspath(self.config_file_path))

        if self.hs_version == 'v2':
            # Write frontend service torrc
            master_torrc_path = os.path.join(self.master_dir, 'torrc-server')
            master_torrc_template = pkg_resources.resource_string(__name__,
                                                                  'data/torrc-server')
            with open(master_torrc_path, "w") as master_torrc_file:
                master_torrc_file.write(master_torrc_template.decode('utf-8'))


def parse_cmd_args():
    """
    Parses and returns command line arguments for config generator
    """

    parser = argparse.ArgumentParser(
        description="onionbalance-config generates config files and keys for "
        "OnionBalance instances and management servers. Calling without any "
        "options will initiate an interactive mode.")

    parser.add_argument("--hs-version", type=str,
                        default="v3",
                        help="Onion service version (default: %(default)s).")

    parser.add_argument("--key", type=str, default=None,
                        help="RSA private key for the master onion service.")

    parser.add_argument("-p", "--password", type=str, default=None,
                        help="Optional password which can be used to encrypt"
                        "the master service private key.")

    parser.add_argument("-n", type=int, default=2, dest="num_instances",
                        help="Number of instances to generate (default: "
                        "%(default)s).")

    parser.add_argument("-t", "--tag", type=str, default='node',
                        help="Prefix name for the service instances "
                        "(default: %(default)s).")

    parser.add_argument("--output", type=str, default='config/',
                        help="Directory to store generate config files. "
                        "The directory will be created if it does not "
                        "already exist.")

    parser.add_argument("--no-interactive", action='store_true',
                        help="Try to run automatically without prompting for"
                        "user input.")

    parser.add_argument("-v", type=str, default="info", dest='verbosity',
                        help="Minimum verbosity level for logging. Available "
                        "in ascending order: debug, info, warning, error, "
                        "critical).  The default is info.")

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

    logger.info("Beginning OnionBalance config generation.")

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
