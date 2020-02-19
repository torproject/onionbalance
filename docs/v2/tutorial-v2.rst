.. _tutorial_v2:

Onionbalance v2 Installation Guide
=======================================

.. toctree::
   :titlesonly:

   installing_ob
   installing_tor
   running-onionbalance
   in-depth
   design

OnionBalance implements `round-robin` like load balancing on top of Tor
onion services. A typical OnionBalance deployment will incorporate one management
servers and multiple backend application servers.

Architecture
------------

The management server runs the OnionBalance daemon. OnionBalance combines the routing information (the introduction points) for multiple backend onion services instances and publishes this information in a master descriptor.

.. image:: ../../onionbalance.png

The backend application servers run a standard Tor onion service. When a client connects to the public onion service they select one of the introduction points at random. When the introduction circuit completes the user is connected to the corresponding backend instance.

**Management Server**
  is the machine running the OnionBalance daemon. It needs to have access to the onion
  service private key corresponding for the desired onion address. This is the public onion address that users will request.

  This machine can be located geographically isolated from the machines
  hosting the onion service content. It does not need to serve any content.

**Backend Instance**
  Each backend application server runs a Tor onion service with a unique onion service key.

.. note::
    The :ref:`onionbalance-config <onionbalance_config>` tool can be used to
    quickly generate keys and config files for your OnionBalance deployment.


The OnionBalance tool provide two command line tools:

 **onionbalance** acts as a long running daemon.

 **onionbalance-config** is a helper utility which eases the process of
 creating keys and configuration files for onionbalance and the backend
 Tor instances.

Getting Started
----------------

To get started with setting up OnionBalance, please go to :ref:`installing_ob`.
