# Onionbalance

![Onionbalance](assets/onionbalance.jpg)

## Overview

[Onionbalance][] is the best way to load balance [Onion Services][] across
multiple backend Tor instances. This way the load of introduction and
rendezvous requests gets distributed across multiple hosts. Onionbalance
provides load-balancing while also making onion services more resilient
and reliable by eliminating single points-of-failure.

Onionbalance allows for scaling across multiple onion service instances
with no additional software or Tor modifications necessary on the onion
service instance.

[Onionbalance]: https://gitlab.torproject.org/tpo/onion-services/onionbalance
[Onion Services]: https://community.torproject.org/onion-services
