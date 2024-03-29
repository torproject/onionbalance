.. image:: obv3_logo.jpg

Onionbalance
============

Introduction
------------

Onionbalance allows Tor onion service requests to be distributed across
multiple backend Tor instances. Onionbalance provides load-balancing while also
making onion services more resilient and reliable by eliminating single
points-of-failure.

|build-status| |docs|

Getting Started
---------------

Installation and usage documentation is available at https://onionbalance.readthedocs.org.

Contact
-------

This software is under active development and likely contains bugs. Please
open bug reports on GitLab if you discover any issues with the software or
documentation.

::

    pub   rsa4096/0x0B67F75BCEE634FB 2022-02-03 [SC] [expires: 2024-01-07]
          Key fingerprint = AD41 7800 1C4C B1DB 0587  12D0 0B67 F75B CEE6 34FB
    uid                   [ultimate] Silvio Rhatto <rhatto@torproject.org>
    sub   rsa4096/0x2C66AD5343667625 2022-02-03 [E] [expires: 2024-01-07]

The Onionbalance software was originally authored and maintained by Donncha Ó
Cearbhaill, and was later maintained by George Kadianakis. Thanks for all the
code!!!

.. |build-status| image:: https://img.shields.io/travis/asn-d6/onionbalance.svg?style=flat
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/asn-d6/onionbalance

.. |coverage| image:: https://coveralls.io/repos/github/asn-d6/onionbalance/badge.svg?branch=master
    :alt: Code coverage
    :target: https://coveralls.io/github/asn-d6/onionbalance?branch=master

.. |docs| image:: https://readthedocs.org/projects/onionbalance-v3/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://onionbalance.readthedocs.org/en/latest/
