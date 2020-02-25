import sys
import signal
import logging

from onionbalance.common import log

logger = log.get_logger()


class SignalHandler(object):
    """
    Handle signals sent to the OnionBalance daemon process
    """

    def __init__(self, controller, status_socket=None):
        """
        Setup signal handler
        """
        self._tor_controller = controller
        self._status_socket = status_socket

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_sigint_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigint_sigterm)

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
