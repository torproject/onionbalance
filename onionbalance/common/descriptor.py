import stem

from onionbalance.common import log

logger = log.get_logger()


def upload_descriptor(controller, signed_descriptor, hsdirs=None, v3_onion_address=None):
    """
    Upload descriptor via the Tor control port

    If no HSDirs are specified, Tor will upload to what it thinks are the
    responsible directories

    If 'v3_onion_address' is set, this is a v3 HSPOST request, and the address
    needs to be embedded in the request.
    """
    logger.debug("Beginning service descriptor upload.")

    server_args = ""

    # Provide server fingerprints to control command if HSDirs are specified.
    if hsdirs:
        server_args = ' '.join([("SERVER={}".format(hsdir))
                                for hsdir in hsdirs])

    if v3_onion_address:
        server_args += " HSADDRESS=%s" % v3_onion_address.replace(".onion", "")

    # Stem will insert the leading + and trailing '\r\n.\r\n'
    response = controller.msg("HSPOST %s\n%s" %
                              (server_args, signed_descriptor))

    (response_code, divider, response_content) = response.content()[0]
    if not response.is_ok():
        if response_code == "552":
            raise stem.InvalidRequest(response_code, response_content)
        else:
            raise stem.ProtocolError("HSPOST returned unexpected response "
                                     "code: %s\n%s" % (response_code,
                                                       response_content))
