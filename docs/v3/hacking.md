# Onionbalance v3 Hacking Guide

This is a small pocket guide to help with maintaining Onionbalance.

## Hacking History

Let's start with some history. Onionbalance (OB) was invented by
Donncha during a GSoC many moons ago. Back then OB only supported v2
onion services. When v3 onions appeared, the Tor network team took over
to [add v3
support](https://gitlab.torproject.org/tpo/core/tor/-/issues/26768).

## How Onionbalance works

Onionbalance is a pretty simple creature.

After it boots and figures how many *frontend services* and *backend
instances* it supports, all it does is spin. While spinning, it
continuously fetches the descriptors of its *backend instances* to check
if something changed (e.g. an intro point rotated, or an instance went
down). When something changes or enough time passes it publishes a new
descriptor for that frontend service. That's all it does really: it
makes sure that its *frontend services* are kept up to date and their
descriptors are always present in the right parts of the hash ring.

## Codebase structure

Onionbalance supports both v3 onions. v2 support has been removed.
`onionbalance/hs_v3` which contains v3-specific code. There is also some
helper functions in `onionbalance/common`. We only care about v3 code in
this document.

Everything starts in `manager.py`. It initializes the *scheduler* (more
on that later) and then instantiates an `onionbalance.py:Onionbalance`
object which is a global singleton that keeps track of all runtime state
(e.g. frontend services, configuration parameters, controller sockets,
etc.).

Each *frontend service* is represented by an `OnionbalanceService`
object. The task of an `OnionbalanceService` is to keep track of the
underlying *backend instances* (which are `InstanceV3` objects) and to
check whether a new descriptor should be uploaded and do to the actual
upload when the time comes.

The *scheduler* initialized by `manager.py` is responsible for
periodically invoking functions that are essential for Onionbalance's
functionality. In particular, those functions fetch the descriptors of
the *backend instances* (`fetch_instance_descriptors`) and publish
descriptors for the *frontend services* (`publish_all_descriptors`).

Another important part of the codebase, is the stem controller in
`onionbalance/hs_v3/stem_controller.py`. The stem controller
is responsible for polling the control port for information (e.g.
descriptors) and also for listening to essential control port events. In
particular, the stem controller will trigger callbacks when a new
consensus or onion service descriptor is downloaded. These callbacks are
important since onionbalance needs to do certain moves when new
documents are received (for example see `handle_new_status_event()` for
when a new consensus arrives).

Finally, the files `consensus.py` and `hashring.py` are responsible for
maintaining the HSv3 hash ring which is how OBv3 learns the right place
to fetch or upload onion service descriptors. The file `params.py` is
where the all magic numbers are kept.

## What about onionbalance-config?

Right. `onionbalance-config` is a tool that helps operators create valid
OBv3 configuration files. It seems like people like to use it, but this
might be because OBv3's configuration files are complicated, and we
could eventually replace it with a more straightforward config file
format.

In any case, the `onionbalance-config` codebase is in
`onionbalance/config_generator` provides a helpful wizard for the user
to input her preferences.

## Is there any cryptography in OBv3?

When it comes to crypto, most of it is handled by stem (it's the one
that signs descriptor) and by tor (it's the one that does all the HSv3
key exchanges, etc.). However, a little bit of magic resides in
`tor_ed25519.py`... Magic is required because Tor uses a different
ed25519 private key format than most common crypto libraries because of
*v3 key blinding*. To work around that, we created a duck-typed wrapper
class for Tor ed25519 private keys; this way hazmat (our crypto lib) can
work with those keys, without ever realizing that it's a different
private key format than what it likes to use. For more information, see
that file's documentation and this [helpful blog
post](https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/).
