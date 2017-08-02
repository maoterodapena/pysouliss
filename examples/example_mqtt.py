"""Example for using pysouliss."""
import souliss as souliss
from optparse import OptionParser
import logging
import paho.mqtt.client as mqtt  # pip install paho-mqtt
import sys

_LOGGER = logging.getLogger(__name__)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    _LOGGER.debug("Connected to mqtt broker with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("pysouliss/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global SOULISS
    _LOGGER.debug("Received "+msg.topic+" "+str(msg.payload))

    # TODO: Caution! No control about messages. This is just a demo
    # and only works with T11
    try:
        (prefix, node, typical, action) = msg.topic.split("/")
    except:
        _LOGGER.error("Message not is not like 'pysouliss/nodenum/typicalnum/action'")
        return False

    if action == 'set':
        _LOGGER.debug("Put %s on node %s / typical %s", msg.payload, node, typical)
    elif action == 'get':
        _LOGGER.debug("Get value on node %s / typical %s", node, typical)
    else:
        _LOGGER.error("Action must be 'set' or 'get'")

def set_main_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-g", "--gateway", dest="gateway",
                      help="Souliss gateway host or IP")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")

    (options, args) = parser.parse_args()
    if options.gateway is None:
        parser.error("You need to provide a gateway host or IP")

    if options.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    return options

if __name__ == "__main__":

    # Parse command line options
    options = set_main_options()

    # Try to connect to souliss gateway
    SOULISS = souliss.Souliss(options.gateway)
    ok = SOULISS.database_structure_request()
    if ok is False:
        _LOGGER.error("Could not connect to souliss gateway at " + gateway)
        sys.exit(1)

    # Try to connect mqtt broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect("localhost", 1883, 60)
    except:
        _LOGGER.error("Could not connect to souliss mqtt broker")
        sys.exit(1)

    client.loop_start()  # starts listening mqtt events

    SOULISS.subscribe_all_typicals(0)  # subscribe to all typicals on node 0
    while True:
        SOULISS.get_response()
