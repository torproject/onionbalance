# Onionbalance Troubleshooting

Here are a few common issues you might encounter during your Onionbalance
setup.

## Permission issues

In order for this to work, the user you are trying to run Onionbalance
from should have permissions to reach Tor's control port cookie.
Otherwise, you will see an error like this:

```
[ERROR]: Unable to authenticate on the Tor control connection: Authentication failed: unable to read '/run/tor/control.authcookie' ([Errno 13] Permission denied: '/run/tor/control.authcookie')
```

As always, we do not recommend running anything as root, when you don't
really have to. In Debian, Tor is run by its dedicated user
`debian-tor`, but it's not the same for other GNU/Linux distributions, so
you need to check. In Debian you can add the user you are running
onionbalance from to the same sudoers group in order to gain permission:

```bash
sudo adduser $USER debian-tor
```

## Failed to read ob_config

The following error might mean that you tried to enable Onionbalance in the backend
without creating the Onion Service first:

```
[notice] Read configuration file "/etc/tor/torrc".
[warn] Could not open "/var/lib/tor/onion_service//ob_config": No such file or directory
[warn] OnionBalance: Unable to read config file "/var/lib/tor/onion_service//ob_config"
[warn] Failed to parse/validate config: Failed to configure rendezvous options. See logs for details.
[err] Reading config failed--see warnings above
```

This can be fixed by first setting up the Onion Service and make sure it's
working, and only then setting `HiddenServiceOnionbalanceInstance 1` as
explained above.

## Invalid INTRO2 keys

If there's a mismatch in the keys defined in the publisher/frontend and the
backend instances -- say the frontend address is
`w37g73bj34w4ms3kiqncab4lshncfihl7nyiqm3te7knxcqx6ljtzkad.onion` while in the
backends the `MasterOnionAddress` is set to a different address like
`5rzgs6g4i4zyo56qpbarbkuqm25mcg2zuqv3si5mtd6t7w4bycirriad.onion` --, then you
might get invalid INTRO2 keys errors like these and your connection attempts
to the main address will timeout:

```
Tor[30478]: Could not get valid INTRO2 keys on circuit 2603341821 for service [scrubbed]
Tor[30478]: Could not get valid INTRO2 keys on circuit 2603341821 for service [scrubbed]
Tor[30478]: Could not get valid INTRO2 keys on circuit 3369496953 for service [scrubbed]
```

This should be fixed by making sure the .onion addresses from both the frontend/publisher
node and the backend instances match each other accordingly.
