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
      --hs-version {v3}     Onion service version (only v3 is supported).
      --key KEY             RSA private key for the master onion service.
      -p, --password PASSWORD
                            Optional password which can be used to encrypt the
                            master service private key.
      -n NUM_INSTANCES      Number of instances to generate (default: 2).
      -s NUM_SERVICES       Number of services to generate (default: 1).
      -t, --tag TAG         Prefix name for the service instances (default: node).
      --output OUTPUT       Directory to store generate config files. The
                            directory will be created if it does not already exist
                            (default: config/).
      --no-interactive      Try to run automatically without prompting for user
                            input.
      -v VERBOSITY          Minimum verbosity level for logging. Available in
                            ascending order: debug, info, warning, error,
                            critical) (default: info).
      --service-virtual-port SERVICE_VIRTUAL_PORT
                            Onion service port for external client connections
                            (default: 80).
      --service-target SERVICE_TARGET
                            Target IP and port where your service is listening
                            (default: 127.0.0.1:80).
      --version             show program's version number and exit


When called without any arguments, the config generator will run in an
interactive mode and prompt for user input.

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


## FILES

onionbalance-config generates the following files:

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

By default, onionbalance-config writes these files in the config/ folder,
relative to the folder where it was invoked from.

The actual folder can be explicitly set by invoking onionbalance-config with the
`--output` flag.

To configure the system-wide service, onionbalance-config should set `--output`
to /etc/onionbalance.

## EXIT STATUS

onionbalance-config exits with a non-zero status in case of errors.

Exit status is 2 on command line invocation errors.

For other, general errors, the exit status is 1.

Otherwise, the exit status is 0.

## AUTHOR

George Kadianakis, Donncha O'Cearbhaill, Silvio Rhatto `<rhatto@torproject.org>`

## SEE ALSO

The *docs/* folder distributed with Onionbalance contains the full documentation,
which should also be available at `<https://onionservices.torproject.org/apps/web/onionbalance/>`.

The Onionbalance source code and all documentation may be downloaded from
`<https://gitlab.torproject.org/tpo/onion-services/onionbalance>`.
