# Onionbalance manual page

## NAME

Onionbalance - an Onion Service descriptor publisher that works as a load balancer

## SYNOPSIS

onionbalance [-h] [--hs-version {v3}] [-i IP] [-p PORT] [-s SOCKET]
                    [-c CONFIG] [-v VERBOSITY] [--version] [--is-testnet]


## DESCRIPTION

Onionbalance allows load balancing Onion Services across multiple backend Tor
instances. This way the load of introduction and rendezvous requests gets
distributed across multiple hosts.

Onionbalance provides load-balancing while also making Onion Services more
resilient and reliable by eliminating single points-of-failure and by
protecting the main identity key.

Onionbalance allows for scaling across multiple Onion Service instances with no
additional software or Tor modifications necessary on the Onion Service
instance.

## FULL INVOCATION

    onionbalance [-h] [--hs-version {v3}] [-i IP] [-p PORT] [-s SOCKET]
                        [-c CONFIG] [-v VERBOSITY] [--version] [--is-testnet]

    onionbalance distributes the requests for a Tor hidden services across
    multiple Tor instances.

    options:
      -h, --help            show this help message and exit
      --hs-version {v3}     Onion service version (only v3 is supported)
      -i, --ip IP           Tor controller IP address (default: 127.0.0.1).
      -p, --port PORT       Tor controller port (default: 9051).
      -s, --socket SOCKET   Tor unix domain control socket location (default:
                            /var/run/tor/control).
      -c, --config CONFIG   Config file location (default: config.yaml).
      -v, --verbosity VERBOSITY
                            Minimum verbosity level for logging. Available in
                            ascending order: debug, info, warning, error,
                            critical) (default: info).
      --version             show program's version number and exit
      --is-testnet          Is this onionbalance on a test net? (Default: no)


## CONFIGURATION

The onionbalance-config(1) tool is the fastest way to generate the necessary keys
and config files to get your onion service up and running.

## CONFIGURATION FILE FORMAT

This is a sample configuration file that can be adapted:

    # Onion Load Balancer Config File example
    #
    # Each Onion Service key line should be associated with a list of 0 or more
    # instances which contain the onion address of the load balancing backend
    # service.

    services:
    - instances: # web
      - address: wmilwokvqistssclrjdi5arzrctn6bznkwmosvfyobmyv2fc3idbpwyd.onion
        name: web1
      - address: fp32xzad7wlnpd4n7jltrb3w3xyj23ppgsnuzhhkzlhbt5337aw2joad.onion
        name: web2
      key: lsainlbvqg6obox2xkcmlv65rlctarxzuzod4juicfj6cstmoimkxyyd.key
    - instances: # irc
      - address: drdoqmg4p43tbtoqxuxs2ax2vgfpetqtvgnpdugh5b2i7f7zxrzvy7id.key
        name: irc1
      - address: u6uoeftsysttxeheyxtgdxssnhutmoo2y2rw6igh5ez4hpxaz4dap7ad.onion
        name: irc2
      key: 6kjmifbfmd2232gpsu7am2psp2ydennc4zhq53zcwlirps5jmpnaikyd.key


The services section of the configuration file contains a list of main Onion
Services that Onionbalance is responsible for.

Each key option specifies the location of the private key for the onion
service. This main private key determines the address that users will use to
access your onion service. This private key must be kept secure.

The location of the private key is evaluated as an absolute path, or relative
to the configuration file location.

You can use existing Tor onion service private key with Onionbalance to keep
your onion address.

Each backend Tor onion service instance is listed by its unique onion address
in the instances list.

NOTE:
:  You can replace backend instance keys if they get lost or compromised.
   Simply start a new backend onion service under a new key and replace the
   address in the config file.

If you have used the onionbalance-config tool you can simply use the generated
config file from config/config.yaml.

NOTE:
:  By default onionbalance will search for a config.yaml file in the current
   working directory.

## FILES

Onionbalance requires the following files:

config.yaml
:  This is the configuration file that is used by the Onionbalance management
   server.

ONION_ADDRESS.key
:  Each service instance have a private key, which will be derived into the
   public address and identity for the Onion Service.
   Each private key file is named after the .onion address, so
   ONION_ADDRESS.key will be actually like
   dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.key.
   It is essential that you keep this file secure.

By default, onionbalance search for these files in the current directory
where it was invoked.

The actual folder can be explicitly set by invoking onionbalance with the
`-c` flag.

When running the system-wide service, this folder is automatically set
to /etc/onionbalance.

## RUNNING

You can start the Onionbalance management server once all of your backend onion
service instances are running.

You will need to create a configuration file which list the backend onion
services and the location of your hidden service keys.

    $ onionbalance -c config.yaml

or

    $ sudo service onionbalance start

The management server must be left running to publish new descriptors for your
onion service: in about 10 minutes you should have a fully functional
onionbalance setup.

NOTE:
:  Multiple Onionbalance management servers can be run simultaneously with
   the same main private key and configuration file to provide redundancy.

## ENVIRONMENT VARIABLES

<!-- This behavior was not ported to v3 Onion Services -->
<!--
The loaded configuration file takes precedence over environment variables.
Configuration file options will override environment variable which have the
same name.
-->

ONIONBALANCE_CONFIG
:  Override the location for the Onionbalance configuration file.

ONIONBALANCE_LOG_LEVEL
:  Specify the minimum verbosity of log messages to output. All log messages
   equal or higher the the specified log level are output. The available log
   levels are the same as the `--verbosity` command line option.

ONIONBALANCE_STATUS_SOCKET_LOCATION
:  The Onionbalance service creates a Unix domain socket which provides
   real-time information about the currently loaded service and descriptors. This
   option can be used to change the location of this domain socket. (default:
   /var/run/onionbalance/control)

ONIONBALANCE_TOR_CONTROL_SOCKET
:  The location of the Tor unix domain control socket. Onionbalance will
   attempt to connect to this control socket first before falling back to using a
   control port connection. (default: /var/run/tor/control)

## EXIT STATUS

Onionbalance is meant to be kept running in the background.

In case of unrecoverable errors, the exit status is 1.
Otherwise, the exit status is 0.

## LIMITATIONS

Onionbalance currently has the following limitations:

1. Only supports the legacy C Tor implementation.

2. Currently does not work along Tor's Proof of Work (PoW) defense for Onion
   Services.

3. For other limitations, check the list of issues available at the
   Onionbalance source code repository and the online documentation.

## AUTHOR

George Kadianakis, Donncha O'Cearbhaill, Silvio Rhatto `<rhatto@torproject.org>`

## SEE ALSO

The *docs/* folder distributed with Onionbalance contains the full documentation,
which should also be available at `<https://onionservices.torproject.org/apps/web/onionbalance/>`.

The Onionbalance source code and all documentation may be downloaded from
`<https://gitlab.torproject.org/tpo/onion-services/onionbalance>`.
