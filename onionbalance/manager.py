#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Global entry point to decide whether we are doing v2 or v3 so that we use the
right codebase
"""

from onionbalance.common import argparser
from onionbalance.common import log
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

import onionbalance.hs_v2.manager
import onionbalance.hs_v3.manager

from onionbalance import __version__

logger = log.get_logger()


def main():
    setproctitle('onionbalance')
    parser = argparser.get_common_argparser()
    args = parser.parse_args()

    logger.warning("Initializing onionbalance (version: %s)...", __version__)

    if args.hs_version == 'v2':
        onionbalance.hs_v2.manager.main(args)
    else:
        onionbalance.hs_v3.manager.main(args)
