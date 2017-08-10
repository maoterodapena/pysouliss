import souliss as souliss
import paho.mqtt.client as mqtt
import logging
import sys

_LOGGER = logging.getLogger(__name__)


class souliss_mqtt:

    """
    Constructor: connects to souliss gateway and mqtt broker, and
    sets on_connect and on_message callbacks for mqtt
    """
    def __init__(self, souliss_gateway,
                 mqtt_broker_ip, mqtt_broker_port=1883):

        self.is_connected = False

        # Try to connect to Souliss
        self.souliss = souliss.Souliss(souliss_gateway)
        self.souliss.database_structure_request()
        self.souliss.get_response()
        if not self.souliss.is_connected():
            _LOGGER.error("Could not connect to souliss gateway at " + souliss_gateway)
            return None

        self.souliss.set_typical_update_callback(self.publish_change)

        # Try to connec to mqtt broker
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        try:
            self.mqttc.connect(mqtt_broker_ip, mqtt_broker_port, 60)
        except:
            _LOGGER.error("Could not connect to souliss mqtt broker. %s" %
                          (sys.exc_info()[1]))
            return None
        _LOGGER.info("Connected to mqtt broker at " + mqtt_broker_ip)

        self.is_connected = True

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        _LOGGER.debug("Connected to mqtt broker with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("pysouliss/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        _LOGGER.debug("Received "+msg.topic+" "+str(msg.payload))

        # TODO: Caution! No control about messages. This is just a demo
        try:
            (prefix, node, typical, action) = msg.topic.split("/")
        except:
            return True

        if action == 'cmd':
            _LOGGER.debug("Send command %s to node %s / typical %s", msg.payload, node, typical)
            self.souliss.send_command(msg.payload, node, typical)
        elif action == 'get':
            _LOGGER.debug("Get value on node %s / typical %s", node, typical)
        else:
            _LOGGER.error("Action must be 'cmd' or 'get'")

    def publish_change(self, typical):
        self.mqttc.publish('pysouliss/%d/%d' % (typical.node, typical.index), typical.state_description)

    def loop_forever(self):
        #self.souliss.subscribe_all_typicals()
        for n in self.souliss.nodes:
            for t in n.typicals:
                t.add_listener(self.publish_change)

        self.mqttc.loop_start()
        while True:
            self.souliss.get_response()
