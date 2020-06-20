import sys
import signal
import logging

from onionbalance.common import log
from onionbalance.hs_v3 import onionbalance as onionbalance_v3

logger = log.get_logger()


class SignalHandler(object):
    """
    Handle signals sent to the OnionBalance daemon process
    """

    def __init__(self, version, controller, status_socket=None):
        """
        Setup signal handler
        """
        self._version = version
        self._tor_controller = controller
        self._status_socket = status_socket

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_sigint_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigint_sigterm)
        if self._version == 'v3':
            signal.signal(signal.SIGHUP, self._handle_sighup)

    def _handle_sigint_sigterm(self, signum, frame):
        """
        Handle SIGINT (Ctrl-C) and SIGTERM

        Disconnect from control port and cleanup the status socket
        """
        logger.info("Signal %d received, exiting", signum)
        self._tor_controller.close()
        if self._status_socket:
            self._status_socket.close()
        logging.shutdown()
        sys.exit(0)

    def _handle_sighup(self, signum, frame):
        """
        Handle SIGHUP (v3 only)

        Reload configuration
        """
        logger.info("Signal SIGHUP received, reloading configuration")
        onionbalance_v3.my_onionbalance.reload_config()
