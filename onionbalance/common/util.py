import sys
import time
import os
import yaml
import stem

from stem.control import Controller

from onionbalance.common import log

logger = log.get_logger()


def read_config_data_from_file(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as handle:
            config_data = yaml.safe_load(handle.read())
            logger.info("Loaded the config file '%s'.", config_path)
    else:
        logger.error("The specified config file '%s' does not exist. The "
                     "onionbalance-config tool can generate the required "
                     "keys and config files.", config_path)
        sys.exit(1)

    return config_data


def connect_to_control_port(tor_socket=None, tor_address=None, tor_port=0, control_password=None):
    controller = None

    # Try first with a connection to the Tor unix domain control socket
    if tor_socket:
        try:
            controller = Controller.from_socket_file(path=tor_socket)
            logger.debug("Successfully connected to the Tor control socket "
                         "%s.", tor_socket)
        except stem.SocketError:
            logger.debug("Unable to connect to the Tor control socket %s.",
                         tor_socket)

    # If we didn't manage to connect to control socket, try IP:PORT
    if not controller:
        try:
            controller = Controller.from_port(address=tor_address,
                                              port=tor_port)
            logger.debug("Successfully connected to the Tor control port.")
        except stem.SocketError as exc:
            logger.error("Unable to connect to Tor control port: %s", exc)
            sys.exit(1)

    try:
        controller.authenticate(password=control_password)
    except stem.connection.AuthenticationFailure as exc:
        logger.error("Unable to authenticate on the Tor control connection: "
                     "%s", exc)
        sys.exit(1)
    else:
        logger.debug("Successfully authenticated on the Tor control "
                     "connection.")

    return controller


def reauthenticate(controller, logger, control_password=None):
    """
    Tries to authenticate to the controller
    """
    time.sleep(10)
    try:
        controller.authenticate(password=control_password)
    except stem.connection.AuthenticationFailure:
        logger.error("Failed to re-authenticate controller.")
