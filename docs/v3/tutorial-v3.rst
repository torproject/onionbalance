.. _tutorial_v3:

Onionbalance v3 Installation Guide
======================================

.. toctree::
   :hidden:

   status-socket

.. contents:: Table of Contents


This is a step-by-step *recipe* to help you configure OnionBalance for v3 onions.

This is really one of my favorite recipes: While onions can make many meals
instantly delicious, if the right balance is not found there is danger that
their strong sulfuric taste can sometimes overpower the rest of the
ingredients. It's vital to maintain the proper onionbalance to really display
the apple-like, deliciously savory notes of this vegetable.

OnionBalance implements `round-robin` like load balancing on top of Tor onion
services. A typical OnionBalance deployment will incorporate one frontend
servers and multiple backend instances.

Preliminaries
-------------

Let's first start with an overview of the Onionbalance design so that you
better understand what we are gonna do in this guide. Through the rest of this
guide we will assume you understand how both onionbalance and the onion service
protocol works. If you already know how onionbalance works, feel free to skip to
:ref:`the next section <overview>`.

.. image:: ./onionbalance_v3.jpg

In this picture you see a setup where OnionBalance is used to load-balance over
three backend instances. The frontend service is on the right side whereas the
three backend instances are in the middle. On the left side there is a Tor
client called Alice who visits the load-balanced service using the frontend
address ``dpkhemrbs3oiv2...onion`` (which is actually 56 characters long but
here we cut it for brevity).

Here is how this works in steps (consult the picture to see where the steps
actually happen):

**[1]:** First the three backend instances (which are regular onion services) publish
     their descriptors to the Tor directory hashring.

**[2]:** Then Onionbalance fetches the descriptors of the backend instances from the hashring.

**[3]:** Onionbalance now extracts the introduction points out of the backend
   descriptors, and creates a new superdescriptor that includes a combination
   of all those introduction points. Then Onionbalance uploads the
   superdescriptor to the hashring.

**[4]:** Now the client, Alice, fetches the superdescriptor from the hashring
   by visiting ``dpkhemrbs3oiv2...onion``.

**[5]:** Alice picks an introduction point from the superdescriptor and
   introduces herself to it. Because the introduction points actually belong to
   the backend instances, Alice is actually talking to backend instance #2,
   effectively getting load-balanced.

The rest of the onion service protocol carries on as normal between the Alice
and the backend instance.

.. _overview:

Overview
-------------

This section will give a short overview of what we are going to do in this
guide.

* We will *start by setting up the frontend host*. We will install Tor and
  onionbalance to it, and then we will run onionbalance so that it generates a
  frontend onion service configuration.

* We will *then setup the backend instances* by configuring Tor as an onion
  service and putting it into "onionbalance instance" mode.

* In the end of the guide, we will *setup onionbalance* by informing it about
  the backend instances, and we will *start it up*. After this, we should have
  a working onionbalance configuration.

Not too hard right? Let's start!

Ingredients
-----------

To follow this recipe to completion we will need the following ingredients:

- a host that will run OnionBalance and act as the load balancing frontend
- two or more hosts tha will run the backend Tor instances

We will assume you are using a Linux system and that you are familiar with
building C and Python projects and installing their dependencies. We will also
assume that you are well familiar with configuring and running Tor onion
services.

Time needed
^^^^^^^^^^^^^^^^

30 minutes

Recipe
-------

Step 1: Configuring the frontend server (setting up Tor)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's start by logging into our frontend server and installing Tor. You will
want a very recent version of Tor (version 0.4.3.1 or newer is sufficient, as
long as it includes `#31684
<https://trac.torproject.org/projects/tor/ticket/31684>`_). If you want to use
the latest official Tor master, you can do the following:

.. code-block:: bash

   $ git clone https://git.torproject.org/tor.git
   $ cd tor
   $ ./autogen.sh && ./configure && make

by the end of this process you should have a Tor binary at
``./src/app/tor``. If this is not the case, you might be missing various C
dependencies like ``libssl-dev``, ``libevent-dev``, etc.

Now setup a minimal torrc with a control port enabled. As an example:

.. code-block:: console

   SocksPort 0
   ControlPort 127.0.0.1:6666
   DataDirectory /home/user/frontend_data/

Now start up Tor and let it do its thing.

Feel free to tweak your torrc as you feel (also enable logging), but for the
purposes of this guide I assume that your control port is at 127.0.0.1:6666.

Step 2: Configuring the frontend server (setting up onionbalance)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, still on the frontend host we need to setup OnionBalance. If you wish to
use the Debian package of onionbalance, you will need version 0.2.0-1 or newer
to get v3 support, otherwise you can obtain it via git:

.. code-block:: bash

   $ git clone https://gitlab.torproject.org/asn/onionbalance.git
   $ cd onionbalance
   $ sudo python3 setup.py install
   # Let's create an onionbalance config file.
   # -n indicates how many empty backend address slots will be created.
   # These can be easily modified with a text editor at any time.
   $ onionbalance-config --hs-version v3 -n 2

After the final command you should have a ``./config/config.yaml`` file
with a basic onionbalance configuration. The onion address of your frontend
service can be found in the bottom of your config file. So if it says

.. code-block:: console

   key: dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.key

the frontend's onion address is: ``dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion`` .

For now, note down the frontend's onion address and let's move on to the next
step!

.. note::

   If you need to migrate an already existing Tor onion service to
   Onionbalance, you can use the `key` directive of the Onionbalance YAML
   config file to point to the onion service's private key
   (`hs_ed25519_secret_key`). You can then use your existing onion service's
   address as your frontend's address.

   So for example if you place your private key in
   `./config/hs_keys/hs_ed25519_secret_key`, your YAML config file might
   contain a `key` directive that looks like this:

      key: hs_keys/hs_ed25519_secret_key

Step 3: Configuring the backend instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OK now with the frontend onion address noted down, let's move to setting up
your backend instances:

Login to one of your backend instances and let's setup Tor. Similar to the step
above, you will need to use the latest Tor master for OnionBalance to work
(because of `#32709 <https://trac.torproject.org/projects/tor/ticket/32709>`_).

As before:

.. code-block:: bash

   $ git clone https://gitweb.torproject.org/tor.git
   $ cd tor
   $ ./autogen.sh && ./configure && make

Now you will need a torrc file for your backend instance. Your torrc file needs
to setup an onion service (and in this case a v3 one) and I'm gonna assume `you
know <https://community.torproject.org/onion-services/setup/>`_ how to do
that. So far so good but here comes the twist:

1) Inside the HiddenService block of your torrc file, you need to add the
   following line: ``HiddenServiceOnionBalanceInstance 1``. Note that if you
   do not have an existing v3 onion service and you are trying to create one
   from scratch, you must first start Tor once without this torrc line, otherwise
   it will fail to start. After the onion service was created, add this line to
   your torrc file.

2) In your hidden service directory where the ``hostname`` and
   ``hs_ed25519_public_key`` files are living (assuming you moved them
   previously or started Tor as described at previous step to generate them)
   you need to create a new file with the name 'ob_config' that has the
   following line inside:

   .. code-block:: console

      MasterOnionAddress dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion

   but substitute the onion address above with your frontend's onion address.

3) Start (or restart if currently running) the Tor process to apply the changes.

The points (1) and (2) above are **extremely important** and if you didn't do
them correctly, nothing is gonna work. If you want to ensure that you did
things correctly, start up Tor, and check that your *notice* log file includes
the following line:

   .. code-block:: console

     [notice] ob_option_parse(): OnionBalance: MasterOnionAddress dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion registered

If you don't see that, then something went wrong. Please try again from the
beginning of this section till you make it! This is the hardest part of the
guide too, so if you can do that you can do anything (fwiw, we are at 75% of
the whole procedure right now).

After you get that, also make sure that your instances are directly reachable
(e.g. using Tor browser). If they are not reachable, then onionbalance won't be
able to see them either and things are not gonna work.

OK, you are done with this backend instance! Now do the same for the other
backend instances and note down the onion addresses of your backend instances
because we are gonna need them for the next and final step.

Step 4: Start onionbalance!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OK now let's login back to the frontend server! Go to your onionbalance config
file and add your instance addresses in the right fields. In the end it should
look like this (for a setup with 3 backend instances):

   .. code-block:: console

      services:
      - instances:
        - address: wmilwokvqistssclrjdi5arzrctn6bznkwmosvfyobmyv2fc3idbpwyd.onion
          name: node1
        - address: fp32xzad7wlnpd4n7jltrb3w3xyj23ppgsnuzhhkzlhbt5337aw2joad.onion
          name: node2
        - address: u6uoeftsysttxeheyxtgdxssnhutmoo2y2rw6igh5ez4hpxaz4dap7ad.onion
          name: node3
        key: dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.key

Backend instances can be added, removed or edited at any time simply by
following the above format. Onionbalance must be restarted after any change of
the config file.

Now let's fire up onionbalance by running the following command (assuming your
`ControlPort` torrc setting is 6666, substitute if different):

   .. code-block:: console

      $ onionbalance -v info -c config/config.yaml -p 6666

If everything went right, onionbalance should start running and after about 10
minutes your frontend service should be reachable via the
``dpkhemrbs3oiv2fww5sxs6r2uybczwijzfn2ezy2osaj7iox7kl7nhad.onion`` address!

If something did not go right, that's OK too, don't get sad because this was
quite complicated. Please check all your logs and make sure you did everything
right according to this guide. Keep on hammering at it and you are gonna get
it. If nothing seems to work, please get in touch with some details and I can
try to help you.

Now What?
--------------------

Now that you managed to make it work, please monitor your frontend service and
make sure that it's reachable all the time. Check your logs for any errors or
bugs and let me know if you see any. If you want you can make onionbalance
logging calmer by using the ``-v warning`` switch.

You can also setup a :ref:`status_socket` to monitor Onionbalance.

If you find bugs or do any quick bugfixes, please submit them over `Gitlab
<https://gitlab.torproject.org/asn/onionbalance>`_ or `Github
<https://github.com/asn-d6/onionbalance>`_!

Troubleshooting
--------------------

Here are a few common issues you might encounter during your setup.

Permission issues
^^^^^^^^^^^^^^^^^^^^

In order for this to work, the user you are trying to run onionbalance from
should have permissions to reach Tor's control port cookie. Othwerise, you will
see an error like this:

   .. code-block:: console

      [ERROR]: Unable to authenticate on the Tor control connection: Authentication failed: unable to read '/run/tor/control.authcookie' ([Errno 13] Permission denied: '/run/tor/control.authcookie')

As always, we do not recommend running anything as root, when you don't really
have to. In Debian, Tor is run by its dedicated user ``debian-tor``, but it's
not the same for other Linux distributions, so you need to check. In Debian you
can add the user you are running onionbalance from to the same sudoers group in
order to gain permission:

   .. code-block:: console

      $ sudo adduser $USER debian-tor
