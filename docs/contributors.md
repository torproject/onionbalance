# Onionbalance contributors

Onionbalance (OB) was invented by Donncha during a GSoC many moons ago. Back
then OB only supported [v2][] Onion Services. When [v3] onions appeared, the Tor
network team took over to [add v3
support](https://gitlab.torproject.org/tpo/core/tor/-/issues/26768).

[v3]: https://spec.torproject.org/rend-spec-v3
[v2]: https://spec.torproject.org/rend-spec-v2

Thank you to the following contributors and others for their invaluble help and
advice in developing Onionbalance along all these years:

* [Donncha Ó Cearbhaill](https://github.com/DonnchaC/)
    * Original author and maintainer of Onionbalance!!!
* [George Kadianakis](https://github.com/asn-d6):
    * Previous Onionbalance maintainer and developer.
* [Federico Ceratto](https://github.com/FedericoCeratto)
    * Tireless assistance with Debian packaging and Onionbalance improvements.
    * Replaced and reimplemented the job scheduler.
    * Implemented support for Unix signals and added a status socket to
      retrieve information about the running service.
* [Michael Scherer](https://github.com/mscherer)
    * Improving the Debian installation documentation.
* [s7r](https://github.com/gits7r)
    * Assisted in testing and load testing Onionbalance from an early stage.
    * Many useful suggestions for performance and usability improvements.
* [Ceysun Sucu](https://github.com/csucu)
    * Added code to reconnect to the Tor control port while Onionbalance is
      running.
* [Alec Muffett](https://github.com/alecmuffett)
    * Extensively tested Onionbalance, found many bugs and made many
      suggestions to improve the software.
* [duritong](https://github.com/duritong)
    * Packaged Onionbalance for Fedora, CentOS, and Redhat 7 (EPEL repository).

Contributions of any kind (code, documentation, testing) are very welcome.
