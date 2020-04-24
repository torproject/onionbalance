.. onionbalance documentation master file, created by
   sphinx-quickstart on Wed Jun 10 13:54:42 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ./../obv3_logo.jpg

Overview
========

OnionBalance is the best way to load balance onion services across multiple
backend Tor instances. This way the load of introduction and rendezvous
requests get distributed across multiple hosts. OnionBalance provides
load-balancing while also making onion services more resilient and reliable by
eliminating single points-of-failure.

- Latest release: |version| (:ref:`changelog`)
- Repository: https://gitlab.torproject.org/asn/onionbalance
- GitHub mirror: https://github.com/asn-d6/onionbalance/
- Issue tracker: https://github.com/asn-d6/onionbalance/issues
- PyPI: https://pypi.org/project/OnionBalance/
- IRC: #tor-dev @ OFTC

Quickstart
============

Onionbalance supports both v2 and v3 onions but because of the different setup
procedure, we have separate guides for them.

See the :ref:`tutorial_v3` page for setting up a v3 onionbalance, or the
:ref:`tutorial_v2` page for setting up a v2 onionbalance.

Table Of Contents
====================

.. toctree::
   :maxdepth: 1
   :titlesonly:

   v3/tutorial-v3
   v2/tutorial-v2
   use-cases
   contributors
   changelog
