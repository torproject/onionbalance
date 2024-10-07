# Onionbalance Use Cases

There a many ways to use Onionbalance to increase the scalability,
reliability and security of your onion service. The following are some
examples of what is possible.

## Examples

* A popular onion service with an overloaded web server or Tor process:
  a service such as Facebook which gets a large number of users would
  like to distribute client requests across multiple servers as the
  load is too much for a single Tor instance to handle. They would
  also like to balance between instances in cases once (and if)
  an [encrypted services proposal][] is implemented[^encrypted-services].

* Redundancy and automatic failover: a political activist would like to keep
  their web service accessible and secure in the event that the secret police
  seize some of their servers. Clients should ideally automatically fail-over
  to another online instances with minimal service disruption.

* Secure Onion Service Key storage: an onion service operator would like to
  compartmentalize their permanent onion key in a secure location separate to
  their Tor process and other services. With this proposal permanent keys could
  be stored on an independent, isolated system.

[encrypted services proposal]: https://gitlab.torproject.org/tpo/core/tor/-/issues/2555
[xxx-encrypted-services]: https://gitlab.torproject.org/tpo/core/torspec/-/blob/main/proposals/ideas/xxx-encrypted-services.txt

[^encrypted-services]: As of 2024-08-05, implementing the
    [xxx-encrypted-services][] proposal is not being planned.

## Known usage

* **SKS Keyserver Pool**: Kristian Fiskerstrand has set up a onion service
  [keyserver pool](https://sks-keyservers.net/overview-of-pools.php#pool_tor)
  which connects users to one of the available onion service key servers.

## Research

[Ceysun Sucu][] has analysed Onionbalance and other approaches to Onion Service
scaling in his masters thesis [Tor: Onion Service Scaling][], which is also
available [this repository][csucu-thesis-repo] along with the [example
experiment][]. The thesis provides a good overview of current approaches. It is
a recommended read for those interested in higher performance Onion Services.

[Ceysun Sucu]: https://github.com/csucu
[Tor: Onion Service Scaling]: https://www.benthamsgaze.org/wp-content/uploads/2015/11/sucu-torscaling.pdf
[csucu-thesis-repo]: https://github.com/csucu/Tor-Hidden-Service-Scaling
[example experiment]: https://github.com/csucu/Tor-Hidden-Service-Scaling/tree/master/example%20experiment
