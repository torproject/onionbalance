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

The `master` directory should be stored on the management server while
the other `instance` directories should be transferred to the respective
backend servers.

## Files

* `master/config.yaml`: This is the configuration file that is used my the
  Onionbalance management server.

* `master/<ONION_ADDRESS>.key`: The private key which will become the public
  address and identity for your onion service. It is essential that you keep
  this key secure.

* `master/torrc-server`: A sample Tor configuration file which can be used with
  the Tor instance running on the management server (v2-only).

* `srv/torrc-instance`: A sample Tor config file which contains the Tor
  `HiddenService*` options needed for your backend Tor instance (v2-only).

* `srv/<ONION_ADDRESS>/private_key`: Directory containing the private key for
  your backend onion service instance. This key is less critical as it can be
  rotated if lost or compromised (v2-only).
