.. _status_socket:

Status Socket
=============

Basic information about running OnionBalance can be obtained by querying
so called status socket.

Status socket is a Unix socket file created by OnionBalance. It is
automatically closed by OnionBalance after reading it to the end.

Example:

.. code-block::

    socat - unix-connect:/var/run/onionbalance/control | json_pp -json_opt pretty
    {
       "services" : [
          {
             "instances" : [
                {
                   "descriptorReceived" : "2020-06-16 19:59:28",
                   "introPointsNum" : 3,
                   "introSetModified" : "2020-06-16 19:59:28",
                   "onionAddress" : "vkmiy6biqcyphtx5exswxl5sjus2vn2b6pzir7lz5akudhwbqk5muead.onion"
                }
             ],
             "onionAddress" : "bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion.onion",
             "publishAttemptFirstDescriptor" : "2020-06-16 20:00:12",
             "publishAttemptSecondDescriptor" : "2020-06-16 20:00:12"
          }
       ]
    }

The overall format of the status socket output is clear from the above
example. Note that `                   "introPointsNum" : 3,
` and `introModified` for an instance is
optional, `uploaded*` and `publishAttempt*` for a service may be `null`.

Meaning of non-self-explanatory fields:

* `introSetModified` is the intro set last modified timestamp.
* `introPointsNum` is the number of introduction points on the descriptor.
* `publishAttemptFirstDescriptor` and `publishAttemptSecondDescriptor` are the last
  publish attempt timestamps for first and second descriptors.
* `descriptorReceived` is the received descriptor timestamp.

Configuration
-------------

Status socket filesystem location can be configured either by
`status-socket-location` in the YAML config file
or by `ONIONBALANCE_STATUS_SOCKET_LOCATION` environment variable
(environment takes precedence).

If neither is given, the socket file is not opened.

Example config file:

.. code-block::

    # OnionBalance Config File
    status-socket-location: /home/user/test.sock
    services:
    - instances:
      - address: vkmiy6biqcyphtx5exswxl5sjus2vn2b6pzir7lz5akudhwbqk5muead.onion
        name: node1
      key: bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.key
