# -*- coding: utf-8 -*-
"""
Provide status over Unix socket
Default path: /var/run/onionbalance/control
"""
import json
import threading
import socket
from socketserver import BaseRequestHandler, ThreadingMixIn, UnixStreamServer

from onionbalance.common import log
from onionbalance.common.status import BaseStatusSocket
from onionbalance.hs_v3.onionbalance import Onionbalance

logger = log.get_logger()


class StatusSocketHandlerMixin(object):
    def __init__(self, balance: Onionbalance):
        self.balance = balance

    def _outputString(self):
        time_format = "%Y-%m-%d %H:%M:%S"
        response = {}
        services_data = []
        for service in self.balance.services:
            instances_data = []
            for instance in service.instances:
                received = instance.descriptor.received_ts.strftime(time_format) \
                    if instance.descriptor else None
                if not instance.intro_set_modified_timestamp:
                    instances_data.append({'onionAddress': instance.onion_address + '.onion',
                                           'received': received})
                else:
                    instances_data.append({'onionAddress': instance.onion_address + '.onion',
                                           'introSetModified': instance.intro_set_modified_timestamp.strftime(time_format),
                                           'introPointsNum': len(instance.descriptor.intro_set),
                                           'descriptorReceived': received})
            if service.first_descriptor:
                last_attempt_first = service.first_descriptor.last_publish_attempt_ts.strftime(time_format)
            else:
                last_attempt_first = None
            if service.second_descriptor:
                last_attempt_second = service.second_descriptor.last_publish_attempt_ts.strftime(time_format)
            else:
                last_attempt_second = None

            services_data.append({'onionAddress': service.onion_address,
                                  'publishAttemptFirstDescriptor': last_attempt_first,
                                  'publishAttemptSecondDescriptor': last_attempt_second,
                                  'instances': instances_data})
        response['services'] = services_data
        return json.dumps(response, sort_keys=True)


class StatusSocketHandlerImpl(BaseRequestHandler, StatusSocketHandlerMixin):
    """
    Handler for new domain socket connections
    """

    def __init__(self, balance: Onionbalance, *args, **kwargs):
        StatusSocketHandlerMixin.__init__(self, balance)
        BaseRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        """
        Prepare and output the status summary when a connection is received
        """
        self.request.sendall(self._outputString().encode('utf-8'))


def create_status_socket_handler(balance: Onionbalance):
    def StatusSocketHandler(*args, **kwargs):
        """
        Fake constructor for StatusSocketHandlerImpl
        """
        return StatusSocketHandlerImpl(balance, *args, **kwargs)

    return StatusSocketHandler


class ThreadingSocketServer(ThreadingMixIn, UnixStreamServer):
    """
    Unix socket server with threading
    """
    pass


class StatusSocket(BaseStatusSocket):
    """
    Create a Unix domain socket which emits a summary of the OnionBalance
    status when a client connects.
    """

    def __init__(self, status_socket_location, balance: Onionbalance):
        """
        Create the Unix domain socket status server and start in a thread

        Example::
            socat - unix-connect:/var/run/onionbalance/control

            {"services": [{"instances": [{"introModified": "2020-06-16 19:35:17", "ipsNum": 3, "onionAddress": "vkmiy6biqcyphtx5exswxl5sjus2vn2b6pzir7lz5akudhwbqk5muead.onion"}], "onionAddress": "bvy46sg2b5dokczabwv2pabqlrps3lppweyrebhat6gjieo2avojdvad.onion.onion", "timestamp": "2020-06-16 19:36:01"}]}
        """
        super().__init__(status_socket_location)

        self.cleanup_socket_file()

        logger.debug("Creating status socket at %s", self.unix_socket_filename)
        try:
            self.server = ThreadingSocketServer(self.unix_socket_filename,
                                                create_status_socket_handler(balance))

            # Start running the socket server in a another thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True  # Exit daemon when main thread stops
            server_thread.start()

        except (OSError, socket.error):
            logger.error("Could not start status socket at %s. Does the path "
                         "exist? Do you have permission?",
                         status_socket_location)
