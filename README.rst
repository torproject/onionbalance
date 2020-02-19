OnionBalance
============

Introduction
------------

The OnionBalance software allows for Tor onion service requests to be
distributed across multiple backend Tor instances. OnionBalance provides
load-balancing while also making onion services more resilient and reliable by
eliminating single points-of-failure.

**This release supports both v2 and v3 onion services and supersedes the
original onionbalance repository**

|build-status| |docs|

Getting Started
---------------

Installation and usage documentation is available at https://onionbalance.readthedocs.org.

Contact
-------

This software is under active development and likely contains bugs. Please
open bug reports on Github if you discover any issues with the software or
documentation.

::
    pub   rsa4096 2012-02-22 [SC]
          13C81580203AE18BB7C0424E09CC7F5315F271D9
    uid           [ultimate] George Kadianakis <asn@torproject.org>
    uid           [ultimate] George Kadianakis <desnacked@riseup.net>
    sub   rsa4096 2012-02-22 [E]


.. |build-status| image:: https://img.shields.io/travis/DonnchaC/onionbalance.svg?style=flat
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/asn-d6/onionbalance

.. |coverage| image:: https://coveralls.io/repos/github/DonnchaC/onionbalance/badge.svg?branch=master
    :alt: Code coverage
    :target: https://coveralls.io/github/asn-d6/onionbalance?branch=master

.. |docs| image:: https://readthedocs.org/projects/onionbalance/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://onionbalance.readthedocs.org/en/latest/
