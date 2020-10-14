import traceback

import stem
from stem.control import EventType
from stem import Signal

import onionbalance.common.util
from onionbalance.common import log

logger = log.get_logger()


def handle_new_status_event_wrapper(status_event):
    """
    A wrapper for this control port event. We need this so that we print
    tracebacks on the listener thread (also see
    https://stem.torproject.org/tutorials/tortoise_and_the_hare.html#advanced-listeners)
    """
    from onionbalance.hs_v3.onionbalance import my_onionbalance
    try:
        my_onionbalance.handle_new_status_event(status_event)
    except BaseException:
        print(traceback.format_exc())


def handle_new_desc_event_wrapper(desc_event):
    """  A wrapper for this control port event (see above) """
    from onionbalance.hs_v3.onionbalance import my_onionbalance
    try:
        my_onionbalance.handle_new_desc_event(desc_event)
    except BaseException:
        print(traceback.format_exc())


def handle_new_desc_content_event_wrapper(desc_content_event):
    """  A wrapper for this control port event (see above) """
    from onionbalance.hs_v3.onionbalance import my_onionbalance
    try:
        my_onionbalance.handle_new_desc_content_event(desc_content_event)
    except BaseException:
        print(traceback.format_exc())


class StemController(object):
    """This class is our interface to the control port"""

    def __init__(self, address=None, port=None, socket=None):
        self.controller = onionbalance.common.util.connect_to_control_port(tor_socket=socket,
                                                                           tor_address=address,
                                                                           tor_port=port)
        assert(self.controller.is_authenticated())

    def mark_tor_as_active(self):
        """
        Send the ACTIVE signal to the control port so that Tor does not become dormant.
        """
        # pylint: disable=no-member
        try:
            self.controller.signal(Signal.ACTIVE)
        except stem.SocketClosed:
            logger.warning("Can't connect to the control port to send ACTIVE signal. Moving on...")

    def get_md_consensus(self):
        return self.controller.get_info("dir/status-vote/current/consensus-microdesc")

    def add_event_listeners(self):
        # pylint: disable=no-member

        self.controller.add_event_listener(handle_new_status_event_wrapper, EventType.STATUS_CLIENT)
        self.controller.add_event_listener(handle_new_desc_event_wrapper, EventType.HS_DESC)
        self.controller.add_event_listener(handle_new_desc_content_event_wrapper, EventType.HS_DESC_CONTENT)

    def shutdown(self):
        self.controller.close()
