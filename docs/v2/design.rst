Design Document
===============

This tool is designed to allow requests to Tor onion service to be
directed to multiple back-end Tor instances, thereby increasing
availability and reliability. The design involves collating the set of
introduction points created by one or more independent Tor onion service
instances into a single 'master' descriptor.

Overview
--------

This tool is designed to allow requests to Tor onion service to be
directed to multiple back-end Tor instances, thereby increasing
availability and reliability. The design involves collating the set of
introduction points created by one or more independent Tor onion service
instances into a single 'master' onion service descriptor.

The master descriptor is signed by the onion service permanent key and
published to the HSDir system as normal.

Clients who wish to access the onion service would then retrieve the
*master* service descriptor and try to connect to introduction points
from the descriptor in a random order. If a client successfully
establishes an introduction circuit, they can begin communicating with
one of the onion services instances with the normal onion service
protocol defined in rend-spec.txt

Instance
  A load-balancing node running an individual onion service.
Introduction Point
  A Tor relay chosen by an onion service instance as a medium-term
  *meeting-place* for initial client connections.
Master Descriptor
  An onion service descriptor published with the desired onion address
  containing introduction points for each instance.
Management Server
  Server running OnionBalance which collates introduction points and
  publishes a master descriptor.
Metadata Channel
  A direct connection from an instance to a management server which can
  be used for instance descriptor upload and transfer of other data.

Retrieving Introduction Point Data
----------------------------------

The core functionality of the OnionBalance service is the collation of
introduction point data from multiple onion service instances by the
management server.

In its basic mode of operation, the introduction point information is
transferred from the onion service instances to the management server
via the HSDir system. Each instance runs an onion service with an
instance specific permanent key. The instance publishes a descriptor to
the DHT at regularly intervals or when its introduction point set
changes.

On initial startup the management server will load the previously
published master descriptor from the DHT if it exists. The master
descriptor is used to prepopulate the introduction point set. The
management server regularly polls the HSDir system for a descriptor for
each of its instances. Currently polling occurs every 10 minutes. This
polling period can be tuned for onion services with shorter or longer
lasting introduction points.

When the management server receives a new descriptor from the HSDir
system, it should before a number of checks to ensure that it is valid:

-  Confirm that the descriptor has a valid signature and that the public
   key matches the instance that was requested.
-  Confirm that the descriptor timestamp is equal or newer than the
   previously received descriptor for that onion service instance. This
   reduces the ability of a HSDir to replay older descriptors for an
   instance which may contain expired introduction points.
-  Confirm that the descriptor timestamp is not more than 4 hours in the
   past. An older descriptor indicates that the instance may no longer
   be online and publishing descriptors. The instance should not be
   included in the master descriptor.

It should be possible for two or more independent management servers to
publish descriptors for a single onion service. The servers would
publish independent descriptors which will replace each other on the
HSDir system.. Any difference in introduction point selection between
descriptors should not impact the end user.

Limitations
'''''''''''

-  A malicious HSDir could replay old instance descriptors in an attempt
   to include expired introduction points in the master descriptor.
   When an attacker does not control all of the responsible HSDirs this
   attack can be mitigated by not accepting descriptors with a timestamp
   older than the most recently retrieved descriptor.

-  The management server may also retrieve an old instance descriptor as
   a result of churn in the DHT. The management server may attempt to
   fetch the instance descriptor from a different set of HSDirs than the
   instance published to.

-  An onion service instance may rapidly rotate its introduction point
   circuits when subjected to a Denial of Service attack. An
   introduction point circuit is closed by the onion service when it has
   received ``max_introductions`` for that circuit. During DoS this
   circuit rotating may occur faster than the management server polls
   the HSDir system for new descriptors. As a result clients may
   retrieve master descriptors which contain no currently valid
   introduction points.

-  It is trivial for a HSDir to determine that a onion service is using
   OnionBalance. OnionBalance will try poll for instance descriptors on a
   regular basis. A HSDir which connects to onion services published to it
   would find that a backend instance is serving the same content as the master
   service. This allows a HSDir to trivially determine the onion addresses for
   a service's backend instances.


Onionbalance allows for scaling across multiple onion service instances with no
additional software or Tor modifications necessary on the onion service
instance. Onionbalance does not hide that a service is using OnionBalance. It
also does not significantly protect a service from introduction point denial of
service or actively malicious HSDirs.


Choice of Introduction Points
-----------------------------

Tor onion service descriptors can include a maximum of 10 introduction
points. OnionBalance should select introduction points so as to
uniformly distribute load across the available backend instances.

Onionbalance will upload multiple distinct descriptors if you have configured
more than 10 instances.

-  **1 instance** - 3 IPs
-  **2 instance** - 6 IPs (3 IPs from each instance)
-  **3 instance** - 9 IPs (3 IPs from each instance)
-  **4 instance** - 10 IPs (3 IPs from one instance, 2 from each other
   instance)
-  **5 instance** - 10 IPs (2 IPs from each instance)
-  **6-10 instances** - 10 IPs (selection from all instances)
-  **11 or more instances** - 10 IPs (distinct descriptors - selection from all instances)

Always attempting to choose 3 introduction points per descriptor may make it
more difficult for a passive observer to confirm that a service is running
OnionBalance. However behavioral characteristics such as the rate of
introduction point rotation may still allow a passive observer to distinguish
an OnionBalance service from a standard Tor onion service.  Selecting a smaller
set of introduction points may impact on performance or reliability of the
service.

-  **1 instance**  - 3 IPs
-  **2 instances** - 3 IPs (2 IPs from one instance, 1 IP from the other
   instance)
-  **3 instances** - 3 IPs (1 IP from each instance)
-  **more than 3 instances** - Select the maximum set of introduction
   points as outlined previously.

It may be advantageous to select introduction points in a non-random
manner. The longest-lived introduction points published by a backend
instance are likely to be stable. Conversely selecting more recently
created introduction points may more evenly distribute client
introductions across an instances introduction point circuits. Further
investigation of these options should indicate if there is significant
advantages to any of these approaches.

Generation and Publication of Master Descriptor
-----------------------------------------------

The management server should generate a onion service descriptor
containing the selected introduction points. This master descriptor is
then signed by the actual onion service permanent key. The signed master
descriptor should be published to the responsible HSDirs as normal.

Clients who wish to access the onion service would then retrieve the
'master' service descriptor and begin connect to introduction points at
random from the introduction point list. After successful introduction
the client will have created an onion service circuit to one of the
available onion services instances and can then begin communicating as
normally along that circuit.
