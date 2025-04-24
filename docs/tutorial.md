# Onionbalance tutorial

This is a step-by-step *recipe* to help you configure Onionbalance for v3
[Onion Services][].

This is really one of my favorite recipes: while onions can make many meals
instantly delicious, if the right balance is not found there is danger that
their strong sulfuric taste can sometimes overpower the rest of the
ingredients. It's vital to maintain the proper onionbalance to really display
the apple-like, deliciously savory notes of this vegetable.

[Onion Services]: https://community.torproject.org/onion-services

## Preliminaries

!!! tip "Optional section"

    If you already know how Onionbalance works, feel free to skip to the
    [Overview](#overview).

Let's first start with an overview of the Onionbalance design so that
you better understand what we are going to do in this guide. Through the
rest of this document we will assume you understand how both Onionbalance
and the [Onion Service][Onion Services] protocol works in overall.

![image](../assets/onionbalance_v3.jpg)

The picture above displays a setup where Onionbalance is used to load-balance
over three backend instances. The frontend service is on the right side whereas
the three backend instances are in the middle. On the left side there is a Tor
client called Alice who visits the load-balanced service using the frontend
address `dpkhemrbs3oiv2...onion` (which is actually 56 characters long but here
we cut it for brevity).

Here is how this works in steps (consult the picture to see where the
steps actually happen):

1. First the three backend instances (which are regular onion services) publish
   their descriptors to the Tor directory hashring.

2. Then Onionbalance fetches the descriptors of the backend instances from
   the hashring.

3. Onionbalance now extracts the introduction points out of the backend
   descriptors, and creates a new superdescriptor that includes a combination
   of all those introduction points. Then Onionbalance uploads the
   superdescriptor to the hashring.

4. Now the client, Alice, fetches the superdescriptor from the hashring
   by visiting `dpkhemrbs3oiv2...onion`.

5. Alice picks an introduction point from the superdescriptor and introduces
   herself to it. Because the introduction points actually belong to the
   backend instances, Alice is actually talking to backend instance #2,
   effectively getting load-balanced.

The rest of the onion service protocol carries on as normal between the
Alice and the backend instance.

## Overview

This section gives a short overview of what we are going to do in this guide.

* We will *start by setting up the frontend host*. We will install Tor and
  Onionbalance to it, and then we will run `onionbalance` so that it generates a
  frontend onion service configuration.
* We will *then setup the backend instances* by configuring Tor as an onion
  service and putting it into "onionbalance instance" mode.
* In the end of the guide, we will *setup onionbalance* by informing it about
  the backend instances, and we will *start it up*. After this, we should have
  a working onionbalance configuration.

Not too hard right? Let's start!

## Ingredients

To follow this recipe to completion we will need the following
ingredients:

* A host that will run Onionbalance and act as the load balancing frontend.
* Two or more hosts that will run the backend Tor instances.

We will assume you are using a GNU/Linux system.
<!--And that you are familiar with building C and Python projects and
installing their dependencies.-->
We will also assume that you are well familiar with configuring and
running Tor [Onion Services][].

## Recipe

### Step 0: Installing the frontend server (setting up Tor)

Let's start by logging into our frontend server and installing a [Tor
daemon][].

You can either:

[Tor daemon]: https://gitlab.torproject.org/tpo/core/tor

1. Install a pre-compiled [Tor daemon][] binary.
2. Build [Tor daemon][] from source.

#### Install a pre-compiled Tor daemon

Depending on your hardware architecture and operating system, a pre-build [Tor
daemon][] package might be available.

In a [Debian][]-like system, you can proceed with the following command:

    sudo apt install tor

[Debian]: https://www.debian.org

#### Build Tor daemon from source

To build the [Tor daemon][] from source, try the latest official version:

<!-- You will want a recent version of Tor (version 0.4.3.1 or newer is
sufficient, as long as it includes
[#31684](https://gitlab.torproject.org/tpo/core/tor/-/issues/31684)). If you
want to use the latest official Tor, you can do the following:-->

```bash
git clone https://git.torproject.org/tor.git
cd tor
./autogen.sh && ./configure && make
```

by the end of this process you should have a Tor binary at
`./src/app/tor`. If this is not the case, you might be missing various C
dependencies like `libssl-dev`, `libevent-dev`, etc.

### Step 1: Configuring the frontend server (configuring Tor)

Now configure a minimal `torrc` file with a control port enabled. As an example:

    SocksPort 0
    ControlPort 127.0.0.1:6666
    DataDirectory /home/user/frontend_data/

If you installed the [Tor daemon][] from a package, this file should be located
on `/etc/tor/torrc`. If you compiled Tor, this file can be anywhere you like.

Now make sure the [Tor daemon][] is running with this configuration:

* When installed via a package, simply reload the `tor` service, usually
  with a command like `sudo service tor restart`.
* When compiled locally, `tor` can be started with `./src/app/tor -c torrc`,
  where `torrc` is the path to the configuration file you created.

Now start up Tor and let it do its thing.

Feel free to tweak your `torrc` as you feel (also enable logging), but for
the purposes of this guide it's assumed that your control port is at
`127.0.0.1:6666`.

### Step 2: Configuring the frontend server (setting up onionbalance)

Now, still on the frontend host we need to setup Onionbalance.

After [installing Onionbalance](installation.md), proceed creating a
configuration:

```bash
onionbalance-config -n 2
```

The `-n` flag indicates how many empty backend address slots should be
created.  These can be easily modified with a text editor at any time.

!!! note

    The [onionbalance-config](config.md) tool can be used to
    quickly generate keys and config files for your Onionbalance deployment.

After the final command you should have a `./config/config.yaml` file
with a basic onionbalance configuration. The onion address of your
frontend service can be found in the bottom of your config file. So if
it says

```yaml
key: dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.key
```

the frontend's onion address is:
`dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion`.

For now, note down the frontend's onion address and let's move on to
the next step!

!!! note

    If you need to migrate an already existing Tor onion service to
    Onionbalance, you can use the `key` directive of the Onionbalance YAML
    config file to point to the onion service's private key
    (`hs_ed25519_secret_key`). You can then use your existing onion service's
    address as your frontend's address.

    So for example if you place your private key in
    `./config/hs_keys/hs_ed25519_secret_key`, your YAML config file might
    contain a `key` directive that looks like this:

    > key: hs_keys/hs_ed25519_secret_key

### Step 3: Configuring the backend instances

OK now with the frontend .onion address noted down, let's move to
setting up your backend instances:

0. Login to one of your backend instances and setup Tor with the same procedure
   detailed on Step 0, but this time for each backend instance.

1. Setup the backend Onion Service [as usual][onion-services-setup].
   After you have installed the [Tor daemon][], you will need a `torrc` file for
   each of your backend instances. Your `torrc` file needs to defined an Onion
   Service and we'll assume [you know][onion-services-setup] how to do that.
   _Make sure it's working before going to the next step_.

2. Inside the `HiddenService` block of your `torrc` file, you need to add
   the following line: `HiddenServiceOnionbalanceInstance 1`.

3. In your hidden service directory where the `hostname` and
   `hs_ed25519_public_key` files are living (assuming you moved them
   previously or started Tor as described at previous point to generate
   them) you need to create a new file with the name `ob_config` that
   has the following line inside:
   `MasterOnionAddress
   dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion`
   but substitute the onion address above with your frontend's onion
   address.

4. Start (or restart if currently running) the Tor process to apply the
   changes.

[onion-services-setup]: https://community.torproject.org/onion-services/setup/

!!! note "Setup the Onion Service first"

    If you do not have an existing Onion Service and you are trying to create
    one from scratch, you must first start Tor once without the
    `HiddenServiceOnionbalanceInstance` option in the `torrc` file, otherwise
    it will fail to start. After the Onion Service was created, add this line
    to your `torrc` file as explained above.

The points 2. and 3. above are **extremely important** and if you
didn't do them correctly, nothing is going to work. If you want to ensure
that you did things correctly, start up Tor, and check that your
*notice* log file includes the following line:

    [notice] ob_option_parse(): Onionbalance: MasterOnionAddress dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion registered

If you don't see that, then something went wrong. Please try again from the
beginning of this section till you make it! This is the hardest part of the
guide too, so if you can do that you can do anything (by the way, we are at 75%
of the whole procedure right now).

After you get that, also make sure that your instances are directly
reachable (e.g. using Tor browser). If they are not reachable, then
Onionbalance won't be able to see them either and things are not going
to work.

OK, you are done with this backend instance! Now do the same for the
other backend instances and note down the onion addresses of your
backend instances because we'll need them for the next and final
step.

### Step 4: Start onionbalance!

OK now let's login back to the frontend server! Go to your onionbalance
config file and add your instance addresses in the right fields. In the
end it should look like this (for a setup with 3 backend instances):

```yaml
services:
- instances:
  - address: wmilwokvqistssclrjdi5arzrctn6bznkwmosvfyobmyv2fc3idbpwyd.onion
    name: node1
  - address: fp32xzad7wlnpd4n7jltrb3w3xyj23ppgsnuzhhkzlhbt5337aw2joad.onion
    name: node2
  - address: u6uoeftsysttxeheyxtgdxssnhutmoo2y2rw6igh5ez4hpxaz4dap7ad.onion
    name: node3
  key: dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.key
```

Backend instances can be added, removed or edited at any time simply by
following the above format. Onionbalance must be restarted after any
change of the config file.

Now let's fire up onionbalance by running the following command
(assuming your `ControlPort` `torrc` setting is `6666`,
substitute if different):

```console
onionbalance -v info -c config/config.yaml -p 6666
```

If everything went right, onionbalance should start running and after
about 10 minutes your frontend service should be reachable via the
`dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion`
address!

If something did not go right, that's OK too, don't get sad because
this was quite complicated. Please check all your logs and make sure you
did everything right according to this guide. Keep on hammering at it
and you are gonna get it. If nothing seems to work, please get in touch
with some details and I can try to help you.

## Now What?

Now that you managed to make it work, please monitor your frontend
service and make sure that it's reachable all the time. Check your logs
for any errors or bugs and let me know if you see any. If you want you
can make onionbalance logging calmer by using the `-v warning` switch.

The management server must be left running to publish new descriptors
for your Onion Service: within minutes you should have a fully
functional onionbalance setup.

You can also setup a [status_socket](socket.md) to monitor Onionbalance.

!!! note

    Multiple Onionbalance management servers can be run simultaneously with the
    same main private key and configuration file to provide redundancy.

## Troubleshooting

There are a few common issues you might encounter during your setup.
Check the [troubleshooting](troubleshooting.md) page for details.
