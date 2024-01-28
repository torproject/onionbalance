#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Global entry point
"""

from onionbalance.common import argparser
from onionbalance.common import log
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

import onionbalance.hs_v3.manager

from onionbalance import __version__

logger = log.get_logger()


def main():
    setproctitle("onionbalance")
    parser = argparser.get_common_argparser()
    args = parser.parse_args()

    logger.warning("Initializing onionbalance (version: %s)...", __version__)
    onionbalance.hs_v3.manager.main(args)
