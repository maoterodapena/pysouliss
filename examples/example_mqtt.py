"""Example for using pysouliss."""
from souliss import souliss_mqtt
from optparse import OptionParser
import logging
import time

_LOGGER = logging.getLogger(__name__)

def set_main_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-g", "--gateway", dest="gateway",
                      help="Souliss gateway host or IP")
    parser.add_option("-m", "--mqtt", dest="mqtt_ip",
                      help="MQTT broker host or IP")
    parser.add_option("-p", "--port", dest="mqtt_port",
                      help="MQTT broker port (default 1883)")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")

    (options, args) = parser.parse_args()
    if options.gateway is None or options.mqtt_ip is None:
        parser.print_help()
        parser.error("ERROR: You need to provide souliss gateway and mqtt IP")

    if options.mqtt_port is None:
        options.mqtt_port = 1883

    if options.verbose:
        FORMAT = "[%(filename)15s:%(lineno)3s - %(funcName)30s() ] %(message)s"
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    return options

if __name__ == "__main__":

    # Parse command line options
    options = set_main_options()

    # Try to connect to souliss gateway
    sm = souliss_mqtt.souliss_mqtt(options.gateway,
                              options.mqtt_ip,
                              options.mqtt_port)
    #a = souliss_mqtt.souliss_mqtt("192.168.1.41", "localhost", 1883)

    time.sleep(1)
    if sm.is_connected:
        sm.loop_forever()
    print("Terminated") 
