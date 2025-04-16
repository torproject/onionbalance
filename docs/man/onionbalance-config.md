# Onionbalance Config manual page

## NAME

Onionbalance - an Onion Service descriptor publisher that works as a load balancer

## SYNOPSIS

onionbalance-config [-h] [--hs-version {v3}] [--key KEY] [-p PASSWORD]
                   [-n NUM_INSTANCES] [-s NUM_SERVICES] [-t TAG]
                   [--output OUTPUT] [--no-interactive] [-v VERBOSITY]
                   [--service-virtual-port SERVICE_VIRTUAL_PORT]
                   [--service-target SERVICE_TARGET] [--version]


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


## CONFIGURATION FILE FORMAT

This is a sample configuration file that can be adapted:



## EXIT STATUS

Onionbalance is meant to be kept running in the background.

In case of unrecoverable errors, the exit status is 1.
Otherwise, the exit status is 0.

## LIMITATIONS

Onionbalance currently has the following limitations:

1. Only supports the legacy C Tor implementation.

2. Does not work along Tor's Proof of Work (PoW) defense for Onion Services.

3. For other limitations, check the list of issues  available at the
   Onionbalance source code repository.

## SEE ALSO

The *docs/* folder distributed with Onionbalance contains the full documentation,
which should also be available at <https://onionservices.torproject.org/apps/web/onionbalance/>.

The Onionbalance source code and all documentation may be downloaded from
<https://gitlab.torproject.org/tpo/onion-services/onionbalance>.
