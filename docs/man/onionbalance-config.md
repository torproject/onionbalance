# Onionbalance Config manual page

## NAME

onionbalance-config - tool for generating onionbalance(1) config files and keys

## SYNOPSIS

onionbalance-config [-h] [--hs-version {v3}] [--key KEY] [-p PASSWORD]
                   [-n NUM_INSTANCES] [-s NUM_SERVICES] [-t TAG]
                   [--output OUTPUT] [--no-interactive] [-v VERBOSITY]
                   [--service-virtual-port SERVICE_VIRTUAL_PORT]
                   [--service-target SERVICE_TARGET] [--version]


## DESCRIPTION

The onionbalance-config tool is the fastest way to generate the necessary keys
and config files to get your onion service up and running.

## FULL INVOCATION

    onionbalance-config [-h] [--hs-version {v3}] [--key KEY] [-p PASSWORD]
                       [-n NUM_INSTANCES] [-s NUM_SERVICES] [-t TAG]
                       [--output OUTPUT] [--no-interactive] [-v VERBOSITY]
                       [--service-virtual-port SERVICE_VIRTUAL_PORT]
                       [--service-target SERVICE_TARGET] [--version]

    onionbalance-config generates config files and keys for Onionbalance instances
    and management servers. Calling without any options will initiate an
    interactive mode.

    options:
      -h, --help            show this help message and exit
      --hs-version {v3}     Onion service version (only v3 is supported.
      --key KEY             RSA private key for the master onion service.
      -p, --password PASSWORD
                            Optional password which can be used to encrypt the
                            master service private key.
      -n NUM_INSTANCES      Number of instances to generate (default: 2).
      -s NUM_SERVICES       Number of services to generate (default: 1).
      -t, --tag TAG         Prefix name for the service instances (default: node).
      --output OUTPUT       Directory to store generate config files. The
                            directory will be created if it does not already
                            exist.
      --no-interactive      Try to run automatically without prompting for user
                            input.
      -v VERBOSITY          Minimum verbosity level for logging. Available in
                            ascending order: debug, info, warning, error,
                            critical). The default is info.
      --service-virtual-port SERVICE_VIRTUAL_PORT
                            Onion service port for external client connections
                            (default: 80).
      --service-target SERVICE_TARGET
                            Target IP and port where your service is listening
                            (default: 127.0.0.1:80).
      --version             show program's version number and exit


When called without any arguments, the config generator will run in an
interactive mode and prompt for user input.

The main directory should be stored on the management server while the other
instance directories should be transferred to the respective backend servers.

## CONFIGURATION FILE FORMAT

This is a sample configuration file that can be adapted:



## FILES

master/config.yaml
:  This is the configuration file that is used my the Onionbalance management
   server.

master/<ONION_ADDRESS>.key
:  The private key which will become the public address and identity for your
   onion service. It is essential that you keep this key secure.

master/torrc-server
:  A sample Tor configuration file which can be used with the Tor instance
   running on the management server (v2-only).

srv/torrc-instance
:  A sample Tor config file which contains the Tor Onion Service options
   needed for your backend Tor instance (v2-only).

srv/<ONION_ADDRESS>/private_key
:  Directory containing the private key for your backend onion service
   instance.  This key is less critical as it can be rotated if lost or
   compromised (v2-only).

## EXIT STATUS

onionbalance-config exits with a non-zero status in case of errors.

Exit status is 2 on command line invocation errors.

For other, general errors, the exit status is 1.

Otherwise, the exit status is 0.

## AUTHOR

George Kadianakis, Donncha O'Cearbhaill, Silvio Rhatto <rhatto@torproject.org>

## SEE ALSO

The *docs/* folder distributed with Onionbalance contains the full documentation,
which should also be available at <https://onionservices.torproject.org/apps/web/onionbalance/>.

The Onionbalance source code and all documentation may be downloaded from
<https://gitlab.torproject.org/tpo/onion-services/onionbalance>.
