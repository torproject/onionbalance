# Onionbalance configuration tool

## Description

The `onionbalance-config` tool is the fastest way to generate the
necessary keys and config files to get your onion service up and
running.

```bash
onionbalance-config
```

When called without any arguments, the config generator will run in an
interactive mode and prompt for user input.

The `config` directory should be stored on the management server.

## Files

Onionbalance requires the following files:

* `config.yaml`: this is the configuration file that is used by the
  Onionbalance management server.

* `ONION_ADDRESS.key`: Each service instance have a private key, which
   will be derived into the public address and identity for the Onion Service.
   Each private key file is named after the .onion address, so
   `ONION_ADDRESS.key` will be actually like
   `dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.key`.
   It is essential that you keep this file secure.

By default, onionbalance search for these files in the current directory
where it was invoked.

The actual folder can be explicitly set by invoking `onionbalance-config` with
the `--output` option.

When running the system-wide service, this folder is automatically set
to `/etc/onionbalance`.

## Environment variables

<!-- This behavior was not ported to v3 Onion Services -->
<!--
The loaded configuration file takes precedence over environment variables.
Configuration file options will override environment variable which have the
same name.
-->

* `ONIONBALANCE_CONFIG`: Override the location for the Onionbalance
  configuration file.

* `ONIONBALANCE_LOG_LEVEL`: Specify the minimum verbosity of log messages to
  output. All log messages equal or higher the specified log level are
  output. The available log levels are the same as the `--verbosity` command
  line option.

* `ONIONBALANCE_STATUS_SOCKET_LOCATION`: The Onionbalance service creates a
  Unix domain socket which provides real-time information about the currently
  loaded service and descriptors. This option can be used to change the
  location of this domain socket. (default: `/var/run/onionbalance/control`).

* `ONIONBALANCE_TOR_CONTROL_SOCKET`: The location of the Tor unix domain
  control socket. Onionbalance will attempt to connect to this control socket
  first before falling back to using a control port connection. (default:
  `/var/run/tor/control`).
