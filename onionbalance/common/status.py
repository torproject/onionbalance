# -*- coding: utf-8 -*-
"""
Base class to provide status over Unix socket
Default path: /var/run/onionbalance/control
"""
import errno
import os

from onionbalance.common import log


logger = log.get_logger()


class BaseStatusSocket(object):
    """
    For creating a Unix domain socket which emits a summary of the OnionBalance
    status when a client connects.
    """
    def __init__(self, unix_socket_filename):
        self.unix_socket_filename = unix_socket_filename

    def cleanup_socket_file(self):
        """
        Try to remove the socket file if it exists already
        """
        try:
            os.unlink(self.unix_socket_filename)
        except OSError as e:
            # Reraise if its not a FileNotFound exception
            if e.errno != errno.ENOENT:
                raise

    def close(self):
        """
        Close the unix domain socket and remove its file
        """
        try:
            self.server.shutdown()
            self.server.server_close()
            self.cleanup_socket_file()
        except AttributeError:
            pass
        except OSError:
            logger.exception("Error when removing the status socket")
