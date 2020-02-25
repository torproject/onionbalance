# -*- coding: utf-8 -*-
from builtins import str, object

from onionbalance.common import log

from onionbalance.hs_v2 import descriptor
from onionbalance.hs_v2 import consensus

logger = log.get_logger()


class EventHandler(object):

    """
    Handles asynchronous Tor events.
    """

    @staticmethod
    def new_status(status_event):
        """
        Parse Tor status events such as "STATUS_CLIENT"
        """
        # pylint: disable=no-member
        if status_event.action == "CONSENSUS_ARRIVED":
            # Update the local view of the consensus in OnionBalance
            try:
                consensus.refresh_consensus()
            except Exception:
                logger.exception("An unexpected exception occured in the "
                                 "when processing the consensus update "
                                 "callback.")

    @staticmethod
    def new_desc(desc_event):
        """
        Parse HS_DESC response events
        """
        logger.debug("Received new HS_DESC event: %s", str(desc_event))

    @staticmethod
    def new_desc_content(desc_content_event):
        """
        Parse HS_DESC_CONTENT response events for descriptor content

        Update the HS instance object with the data from the new descriptor.
        """
        logger.debug("Received new HS_DESC_CONTENT event for %s.onion",
                     desc_content_event.address)

        #  Check that the HSDir returned a descriptor that is not empty
        descriptor_text = str(desc_content_event.descriptor).encode('utf-8')

        # HSDirs provide a HS_DESC_CONTENT response with either one or two
        # CRLF lines when they do not have a matching descriptor. Using
        # len() < 5 should ensure all empty HS_DESC_CONTENT events are matched.
        if len(descriptor_text) < 5:
            logger.debug("Empty descriptor received for %s.onion",
                         desc_content_event.address)
            return None

        # Send content to callback function which will process the descriptor
        try:
            descriptor.descriptor_received(descriptor_text)
        except Exception:
            logger.exception("An unexpected exception occured in the "
                             "new descriptor callback.")

        return None
