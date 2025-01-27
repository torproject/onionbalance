# Onionbalance Hacking Guide

This is a small pocket guide to help with maintaining Onionbalance.

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

Onionbalance supports [v3][] Onion Services ([v2][] support [has been
removed][v2-removed]) through the [hs_v3 package][onionbalance.hs_v3], which
contains [v3][]-specific code. There is also some helper functions in
[onionbalance/common][]. We only care about v3 code in this document.

[v3]: https://spec.torproject.org/rend-spec-v3
[v2]: https://spec.torproject.org/rend-spec-v2
[v2-removed]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/commit/084ce8a15c9a1343fc10f0e75090bf551cb35bba
[onionbalance/common]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/common

Everything starts in [manager.py][]. It initializes the *scheduler* (more
on that later) and then instantiates an [Onionbalance][onionbalance-object]
object which is a global singleton that keeps track of all runtime state
(e.g. frontend services, configuration parameters, controller sockets,
etc.).

[manager.py]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/hs_v3/manager.py
[onionbalance-object]: api.md#onionbalance.hs_v3.onionbalance.Onionbalance

Each *frontend service* is represented by an [OnionbalanceService][]
object. The task of an [OnionbalanceService][] is to keep track of the
underlying *backend instances* (which are [InstanceV3][] objects) and to
check whether a new descriptor should be uploaded and do to the actual
upload when the time comes.

[OnionbalanceService]: api.md#onionbalance.hs_v3.service.OnionbalanceService
[InstanceV3]: api.md#onionbalance.hs_v3.instance.InstanceV3

The *scheduler* initialized by [manager.py][] is responsible for
periodically invoking functions that are essential for Onionbalance's
functionality. In particular, those functions fetch the descriptors of
the *backend instances* ([fetch_instance_descriptors][]) and publish
descriptors for the *frontend services* ([publish_all_descriptors][]).

[fetch_instance_descriptors]: api.md#onionbalance.hs_v3.onionbalance.Onionbalance.fetch_instance_descriptors
[publish_all_descriptors]: api.md#onionbalance.hs_v3.onionbalance.Onionbalance.publish_all_descriptors

Another important part of the codebase, is the [Stem][] controller in
[stem_controller.py][]. The stem controller
is responsible for polling the control port for information (e.g.
descriptors) and also for listening to essential control port events. In
particular, the stem controller will trigger callbacks when a new
consensus or onion service descriptor is downloaded. These callbacks are
important since onionbalance needs to do certain moves when new
documents are received (for example see [handle_new_status_event()][] for
when a new consensus arrives).

[Stem]: https://stem.torproject.org
[stem_controller.py]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/hs_v3/stem_controller.py
[handle_new_status_event()]: api.md#onionbalance.hs_v3.onionbalance.Onionbalance.handle_new_status.event

Finally, the files [consensus.py][] and [hashring.py][] are responsible for
maintaining the HSv3 hash ring which is how OBv3 learns the right place
to fetch or upload onion service descriptors. The file [params.py][] is
where the all magic numbers are kept.

[consensus.py]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/hs_v3/consensus.py
[hashring.py]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/hs_v3/hashring.py
[params.py]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/hs_v3/params.py

## What about onionbalance-config?

Right. [onionbalance-config][] is a tool that helps operators create valid
OBv3 configuration files. It seems like people like to use it, but this
might be because OBv3's configuration files are complicated, and we
could eventually replace it with a more straightforward config file
format.

In any case, the [onionbalance-config][] codebase is in
[onionbalance/config_generator][onionbalance.config_generator], providing a
helpful wizard for the user to input her preferences.

[onionbalance-config]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance-config.py

## Is there any cryptography in OBv3?

When it comes to crypto, most of it is handled by stem (it's the one
that signs descriptor) and by tor (it's the one that does all the HSv3
key exchanges, etc.). However, a little bit of magic resides in
[tor_ed25519.py][]... Magic is required because Tor uses a different
ed25519 private key format than most common crypto libraries because of
*v3 key blinding*. To work around that, we created a duck-typed wrapper
class for Tor ed25519 private keys; this way hazmat (our crypto lib) can
work with those keys, without ever realizing that it's a different
private key format than what it likes to use. For more information, see
that file's documentation and this [helpful blog post][ed25519-keys].

[tor_ed25519.py]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/blob/main/onionbalance/hs_v3/tor_ed25519.py
[ed25519-keys]: https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/
