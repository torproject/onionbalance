.. _installing_tor:

Installing Tor
===============

Installing and Configuring Tor
------------------------------

Tor is need on the management server and every backend onion service
instance.

Management Server
~~~~~~~~~~~~~~~~~

OnionBalance requires that a recent version of Tor (``>= 0.2.7.1-alpha``) is
installed on the management server system. This version might not be available
in your operating system's repositories yet.

It is recommended that you install Tor from the
`Tor Project repositories <https://www.torproject.org/download/download-unix.html.en>`_
to ensure you stay up to date with the latest Tor releases.

The management server need to have its control port enabled to allow
the OnionBalance daemon to talk to the Tor process. This can be done by
uncommenting the ``ControlPort`` option in your ``torrc`` configuration file.

Alternatively you can replace your ``torrc`` file with the following
is suitable for the Tor instance running on the management server:

.. literalinclude:: ../../onionbalance/config_generator/data/torrc-server
   :name: torrc-server
   :lines: 6-

After configuring Tor you should restart your Tor process

.. code-block:: console

    $ sudo service tor reload

Backend Instances
~~~~~~~~~~~~~~~~~

Each backend instance should be run a standard onion service which serves your
website or other content. More information about configuring onion services is
available in the Tor Project's
`onion service configuration guide <https://www.torproject.org/docs/tor-hidden-service.html.en>`_.

If you have used the ``onionbalance-config`` tool you should transfer the
generated instance config files and keys to the Tor configuration directory
on the backend servers.

.. literalinclude:: ../../onionbalance/config_generator/data/torrc-instance-v2
   :name: torrc-instance
   :lines: 6-

After configuring Tor you should restart your Tor process

.. code-block:: console

    $ sudo service tor reload

Now that Tor is installed and configured, please move to :ref:`running_onionbalance`.
