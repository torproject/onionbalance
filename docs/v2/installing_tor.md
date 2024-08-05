# Installing Tor

!!! warning

    This section refers to the older v2 codebase.
    Although outdated, it's still available for historic purposes.

## Installing and Configuring Tor

Tor is need on the management server and every backend onion service
instance.

### Management Server

Onionbalance requires that a recent version of Tor (`>= 0.2.7.1-alpha`)
is installed on the management server system. This version might not be
available in your operating system's repositories yet.

It is recommended that you install Tor from the [Tor Project
repositories](https://www.torproject.org/download/download-unix.html.en)
to ensure you stay up to date with the latest Tor releases.

The management server need to have its control port enabled to allow the
Onionbalance daemon to talk to the Tor process. This can be done by
uncommenting the `ControlPort` option in your `torrc` configuration
file.

Alternatively you can replace your `torrc` file with
[this one suitable for the Tor instance on the management server][].

After configuring Tor you should restart your Tor process

```console
$ sudo service tor reload
```

[this one suitable for the Tor instance on the management server]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/config_generator/data/torrc-server

### Backend Instances

Each backend instance should be run a standard onion service which
serves your website or other content. More information about configuring
onion services is available in the Tor Project's [Onion Service configuration
guide][].

[Onion Service configuration guide]: https://community.torproject.org/onion-services/setup/

If you have used the `onionbalance-config` tool you should transfer the
generated instance config files and keys to the Tor configuration
directory on the backend servers. [Example torrc-instance-v3][].

After configuring Tor you should restart your Tor process:

```console
$ sudo service tor reload
```

Now that Tor is installed and configured, please move to
[Running Onionbalance](running.md).

[Example torrc-instance-v2]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/config_generator/data/torrc-instance-v2
