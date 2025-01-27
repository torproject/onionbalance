# Onionbalanace Security

## Intro

Onionbalance is a load-balancing tool for Tor Onion Services that enhances
scalability and availability by distributing client traffic across multiple
backend instances. While it offers significant advantages, it also introduces
unique security considerations. This document analyzes its key security
benefits, risks, adversary capabilities, and mitigations to help operators
deploy Onionbalance securely. In this analysis, we distinguish between the
Onionbalance instance responsible for creating and uploading the master
descriptor and backend instances, which handle client traffic.

## Key Security Benefits

Onionbalance mitigates several risks inherent in traditional single-instance
Onion Services by introducing architectural changes that isolate critical
components and reduce attack surfaces.

### Master Key Isolation

The master private key for the .onion address is stored exclusively on the
Onionbalance instance, which never directly interacts with clients. This
isolation ensures that:

* Even if a backend instance is compromised, the integrity of the .onion
  address remains intact.
* Administrators can replace compromised backends without impacting the
  Onionbalance .onion address or needing to regenerate keys.

This setup mitigates the risk of service takeover, a common issue in
traditional Onion Services where keys might reside on the same server
handling client traffic.

### Reduced Attack Surface for Onionbalance Instance

The Onionbalance instance only connects to the Tor network during descriptor
uploads, significantly reducing its exposure compared to traditional Onion
Services. Key points include:

* Short-lived connections: unlike standard Onion Services that maintain
  persistent circuits to introduction points and handle client traffic, the
  Onionbalance instance only establishes circuits briefly to upload
  descriptors.
* Fewer circuits: this minimizes the risk of selecting malicious relays and
  reduces opportunities for traffic fingerprinting or correlation attacks.
* No direct client interaction: clients never connect to the Onionbalance
  instance, further reducing its attack surface.

### Enhanced Availability Protection

The distributed backend architecture ensures that:

* If one or more backend instances fail, only their respective introduction
  points are affected. The service as a whole remains operational through other
  backends.
* Backend failures are harder for adversaries to correlate due to the
  distribution of introduction points across multiple locations.

This setup significantly improves resilience compared to single-instance Onion
Services, which can be entirely disabled by a single point of failure.

### Traffic Correlation Resistance

Adversaries monitoring an Onion Service's availability may attempt to correlate
outages with external events (e.g., power failures or intentional disruptions).
With Onionbalance:

* Only introduction points associated with affected backends fail during
  outages, making it harder for adversaries to attribute failures to specific
  servers.
* The use of multiple backend instances (e.g., 10 backends with 3 introduction
  points each) increases the total number of introduction points (30 in this
  case). If one backend fails, only 3 introduction points are affected, while
  clients can still use the remaining 27. This distribution complicates
  correlation attacks.

However, it should be noted that local adversaries capable of blocking
connections at suspected server locations can still perform repeated
correlation attempts until they succeed.

### Recovery Capabilities

* The Onionbalance instance can quickly recover from downtime by fetching
  descriptors from backend instances and re-uploading a fresh master
  descriptor.
* Administrators can deploy secondary Onionbalance instances with separate
  .onion addresses for redundancy or load balancing.
* Backend replacement is seamless and does not require regenerating keys or
  disrupting service continuity.

## Security Considerations

### Descriptor Fingerprinting

Onionbalance does not hide that a service is using
Onionbalance. It also does not significantly protect a service from
introduction point denial of service or actively malicious HSDirs.

Service descriptors uploaded by Onionbalance may reveal its usage due to
structural differences such as:

* Larger descriptor sizes resulting from multiple backends and their associated
  introduction points.
* A higher-than-usual number of introduction points compared to standard
  single-instance Onion Services.

Adversaries analyzing descriptors could infer that multiple .onion addresses
are linked or identify custom configurations unique to a specific deployment.

Mitigation: standardizing descriptor structures within the Onionbalance
codebase could limit adversaries' ability to distinguish between default and
customized deployments[^descriptor-standardization].

[^descriptor-standardization]: As of 2025-01, this is being handled
  on ticket [tpo/onion-services/onionbalance#6][].

[tpo/onion-services/onionbalance#6]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/6

### Synchronization Issues of Backend Instances

Backend instances must coordinate their Tor configurations (e.g., Guard node
selection) to avoid exposing themselves to malicious relays. Without proper
synchronization:

* Each backend independently selects relays, increasing the likelihood of
  encountering malicious nodes across all circuits.
* Circuit-level deanonymization risks rise with more backends operating
  unsynchronized.

### Configuration Complexities

Managing multiple backend instances introduces administrative overhead and
increases the risk of misconfiguration. Examples include:

* Failing to synchronize relay selection or security parameters across
  backends.
* Failing to properly update services.
* Failing to evaluate relevant log files.

### Single Point of Failure

The Onionbalance instance remains a single point of failure for descriptor
uploads.

* Clients will be unable to connect if descriptor uploads fail for extended
  periods.
* If compromised, adversaries can impersonate the service by extracting private
  keys from the instance.

However, short downtimes are less noticeable due to infrequent connections,
and recovery is relatively quick.

### HSDir Targeting

Adversaries may attempt to compromise HSDirs hosting service descriptors. While
this is a general risk for all Onion Services:

* Without knowledge of the .onion address, adversaries cannot identify specific
  services even if they compromise an HSDir.
* Descriptor upload windows are brief, limiting exposure compared to
  traditional services that maintain persistent circuits.

### Vanguards Integration Challenges

* Vanguards' default descriptor size limit (30kB) may conflict with larger
  master descriptors generated by Onionbalance. Operators must carefully
  configure limits without exceeding protocol constraints (50kB).
* Vanguards' optional feature of tearing down introduction point circuits based
  on traffic volume could cause frequent descriptor updates in dynamic
  environments.

## Current Limitations

### No Support for Proof-of-Work Protocol

* [Proof-of-Work (PoW) protocols][pow] enhance resistance against DoS attacks by requiring
  clients to perform computational work before accessing descriptors. Lack of
  support limits protection against high-volume attacks[^onionbalance-pow].

[^onionbalance-pow]: As of 2025-01, [PoW][pow] support in Onionbalance is
  being discussed at [tpo/onion-services/onionbalance#13][].

[tpo/onion-services/onionbalance#13]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/13
[pow]: https://onionservices.torproject.org/technology/pow/

### No Restricted Discovery Support

* Restricted Discovery (formerly known as [Client authorization][client-auth])
  mechanisms (e.g., pre-shared keys) allow access control for sensitive
  services but are currently unsupported by
  Onionbalance[^restricted-discovery].

[^restricted-discovery]: Handled at [tpo/onion-services/onionbalance#5][].

[client-auth]: https://community.torproject.org/onion-services/advanced/client-auth/
[tpo/onion-services/onionbalance#5]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/5

### Suboptimal Load Balancing

In some cases, load distribution across HSDirs may not be optimal due to
limitations in descriptor copying logic. For example:

* If six HSDirs are available but only five descriptors are generated, one
  HSDir will receive duplicate descriptors, leading to uneven workload
  distribution among backends.

### Introduction Point discrepancies

* An Onion Service instance may rapidly rotate its introduction point circuits
  when subjected to a Denial of Service attack. An introduction point circuit
  is closed by the onion service when it has received `max_introductions` for
  that circuit. During DoS this circuit rotating may occur faster than the
  management server polls the HSDir system for new descriptors. As a result
  clients may retrieve main descriptors which contain no currently valid
  introduction points.

### Malicious HSDirs

* A malicious HSDir could replay old instance descriptors in an attempt to
  include expired introduction points in the main descriptor. When an
  attacker does not control all of the responsible HSDirs this attack can be
  mitigated by not accepting descriptors with a timestamp older than the most
  recently retrieved descriptor.
  This attack is very hard to mount, since the set of responsible HSDirs
  [changes at each time period][hashring].
<!--
  The following seems not to be valid anymore for v3 Onion Services, since
  a HSDir cannot know anymore which descriptor belongs to which services,
  and also cannot decrypt the inner descriptor layer.
-->
<!--
* It is also trivial for a HSDir to determine that an Onion Service is using
  Onionbalance. Onionbalance will try poll for instance descriptors on a
  regular basis. A HSDir which connects to Onion Services published to it would
  find that a backend instance is serving the same content as the main service.
  This allows a HSDir to trivially determine the onion addresses for a
  service's backend instances.
-->

[hashring]: https://spec.torproject.org/rend-spec/deriving-keys.html#HASHRING

### No Automatic Reupload Attempts for Failed Descriptors

* If descriptor uploads fail due to network issues or relay unavailability,
  administrators must manually restart the process. Automating reuploads would
  improve reliability[^automatic-reupload].

[^automatic-reupload]: As of 2025-01, this is being tracked
  at [tpo/onion-services/onionbalance#38][].

[tpo/onion-services/onionbalance#38]: https://gitlab.torproject.org/tpo/onion-services/onionbalance/-/issues/38

<!--
  This does not seem to be the case with rend-spec-v3.
-->
<!--
### HSDir churn

!!! note "Needs confirmation"

    The following claim still needs to be confirmed.

* The management server may also retrieve an old instance
  descriptor as a result of churn in the DHT. The management server may attempt
  to fetch the instance descriptor from a different set of HSDirs than the
  instance published to.
  This seems unlikely to happen, as it would require the management server's
  Tor daemon to have an outdated copy of the network consensus.
  And even if that were the case, an old descriptor would probably be already
  expired.
-->

## Credits

This text was originally written by [Pascal Tippe][].

[Pascal Tippe]: https://www.fernuni-hagen.de/pv/en/team/pascal.tippe.shtml

## Notes
