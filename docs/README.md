# Onionbalance

![Onionbalance](assets/onionbalance.jpg)

## Overview

[Onionbalance][] is the best way to load balance [Onion Services][] across
multiple backend Tor instances. This way the load of introduction and
rendezvous requests gets distributed across multiple hosts.

[Onionbalance][] provides load-balancing while also making [Onion Services][]
more resilient and reliable by eliminating single points-of-failure and by
protecting the identity key.

[Onionbalance][] allows for scaling across multiple
[Onion Service][Onion Services] instances with no additional software or Tor
modifications necessary on the Onion Service instance.

[Onionbalance]: https://gitlab.torproject.org/tpo/onion-services/onionbalance
[Onion Services]: https://community.torproject.org/onion-services
