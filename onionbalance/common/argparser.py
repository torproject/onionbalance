import argparse
import os

import onionbalance

TOR_CONTROL_SOCKET = os.environ.get('ONIONBALANCE_TOR_CONTROL_SOCKET',
                                    '/var/run/tor/control')


def get_common_argparser():
    """
    Parses and returns command line arguments.
    """

    parser = argparse.ArgumentParser(
        prog='onionbalance',
        description="onionbalance distributes the requests for a Tor hidden "
        "services across multiple Tor instances.")

    parser.add_argument("--hs-version", type=str, default='v3',
                        choices=('v3',),
                        help="Onion service version (only v3 is supported)")

    parser.add_argument("-i", "--ip", type=str, default='127.0.0.1',
                        help="Tor controller IP address (default: %(default)s).")

    parser.add_argument("-p", "--port", type=int, default=9051,
                        help="Tor controller port (default: %(default)s).")

    parser.add_argument("-s", "--socket", type=str, default=TOR_CONTROL_SOCKET,
                        help="Tor unix domain control socket location (default: %(default)s).")

    parser.add_argument("-c", "--config", type=str,
                        default=os.environ.get('ONIONBALANCE_CONFIG',
                                               "config.yaml"),
                        help="Config file location (default: %(default)s).")

    parser.add_argument("-v", "--verbosity", type=str, default='info',
                        help="Minimum verbosity level for logging.  Available "
                             "in ascending order: debug, info, warning, "
                             "error, critical) (default: %(default)s).")

    parser.add_argument('--version', action='version',
                        version='onionbalance %s' % onionbalance.__version__)

    parser.add_argument("--is-testnet", action='store_true',
                        help="Is this onionbalance on a test net? (Default: no)")

    return parser
