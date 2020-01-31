#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Convenience wrapper for running OnionBalance directly from source tree."""

import onionbalance.hs_v2.manager
import onionbalance.hs_v3.manager

if __name__ == '__main__':
    onionbalance.hs_v3.manager.main()
