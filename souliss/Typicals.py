import logging
import struct

_LOGGER = logging.getLogger(__name__)

typical_types = {
        0x11: {
            "desc": "T11: ON/OFF Digital Output with Timer Option", "size": 1,
            "state_desc": { 0x00: "off",
                            0x01: "on"}
            },
        0x12: {"desc": "T12: ON/OFF Digital Output with AUTO mode", 
            "size": 1,
            "state_desc": { 0x00: "off",
                            0x01: "on",
                            0xF0: "on/auto", 
                            0xF1: "off/auto"
                            }
            },
        0x13: {"desc": "T13: Digital Input Value", 
            "size": 1,
            "state_desc": { 0x00: "off",
                             0x01: "on"}
            },
        0x14: {"desc": "T14: Pulse Digital Output", 
            "size": 1,
            "state_desc": { 0x00: "off",
                             0x01: "on"}
            },
        0x15: {"desc": "T15: RGB Light", 
            "size": 2,
            "state_desc": { 0x00: "off",
                             0x01: "on"}
            },
        0x16: {"desc": "T16: RGB LED Strip", 
            "size": 4,
            "state_desc": { 0x00: "on",
                             0x01: "on"}
            },
        0x18: {"desc": "T18: ON/OFF Digital Output (Step Relay)", 
            "size": 1,
            "state_desc": { 0x00: "off",
                             0x01: "on"}
            },
        0x19: {"desc": "T19: Single Color LED Strip", 
            "size": 2,
            "state_desc": { 0x00: "off",
                             0x01: "on"}
            },
        0x1A: {"desc": "T1A: Digital Input Pass Through", 
            "size": 1,
            "state_desc": { 0x00: "off",
                             0x01: "on"}
            },
        0x1B: {"desc": "T1B: Position Constrained ON/OFF Digital Output", "size": 1},
        0x21: {"desc": "T21: Motorized devices with limit switches", "size": 1},
        0x22: {"desc": "T22: Motorized devices with limit switches and middle position", "size": 1},
        0x31: {"desc": "T31: Temperature control with cooling and heating mode", "size": 5},
        0x32: {"desc": "T32: Air Conditioner", "size": 2},
        0x41: {"desc": "T41: Anti-theft integration -Main-",  "size": 1},
        0x42: {"desc": "T42: Anti-theft integration -Peer-",  "size": 1},
        0x51: {"desc": "T51: Analog input, half-precision floating point", 
            "size": 2,
            "units": "units"},
        0x52: {"desc": "T52: Temperature measure (-20, +50) C", 
            "size": 2,
            "units": "C"},
        0x53: {"desc": "T53: Humidity measure (0, 100) ", 
            "size": 2,
            "units": "%"},
        0x54: {"desc": "T54: Light Sensor (0, 40) kLux", 
            "size": 2,
            "units": "kLux"},
        0x55: {"desc": "T55: Voltage (0, 400) V", 
            "size": 2,
            "units": "V"},
        0x56: {"desc": "T56: Current (0, 25) A", 
            "size": 2,
            "units": "A"},
        0x57: {"desc": "T57: Power (0, 6500) W", 
            "size": 2,
            "units": "W"},
        0x58: {"desc": "T58: Pressure measure (0, 1500) hPa", 
            "size": 2,
            "units": "hPa"},
        0x61: {"desc": "T61: Analog setpoint, half-precision floating point", "size": 2},
        0x62: {"desc": "T62: Temperature measure (-20, +50) C", "size": 2},
        0x63: {"desc": "T63: Humidity measure (0, 100) ", "size": 2},
        0x64: {"desc": "T64: Light Sensor (0, 40) kLux", "size": 2},
        0x65: {"desc": "T65: Voltage (0, 400) V", "size": 2},
        0x66: {"desc": "T66: Current (0, 25) A", "size": 2},
        0x67: {"desc": "T67: Power (0, 6500) W", "size": 2},
        0x68: {"desc": "T68: Pressure measure (0, 1500) hPa", "size": 2}
        }

class Typical(object):
    def __init__(self, ttype):
        self.ttype = ttype
        self.description = typical_types[ttype]['desc']
        self.size = typical_types[ttype]['size']
        self.slot = -1  # undefined until assigned to a slot
        self.node = -1  # undefined until assigned to a slot

        # inital state. It will be overwritten with the first update
        self.state = b'\x00\x00\x00\x00\x00\x00\x00'
        self.listeners = []

    def add_listener(self, callback):
        self.listeners.append(callback)

    @staticmethod
    def factory_type(ttype):
        if ttype in [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x18, 0x19, 0x1A, 0x1B]:
            return TypicalT1n(ttype)
        elif ttype in [0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58]:
            return TypicalT5n(ttype)
        else:
            return TypicalNotImplemented(ttype)

    def update(self, value):
        value = value[:self.size]
        if value != self.state:
            self.state = value
            self.state_description = value
            _LOGGER.info("Node %d: Typical %d - %s updated from %s to %s" % (self.index,
                self.description,
                ':'.join("{:02x}".format(c) for c in self.state[:self.size]),
                ':'.join("{:02x}".format(c) for c in value[:self.size])))

            for listener in self.listeners:
                listener(self)
            """
            if self.mqtt:
                # TODO: este self....
                print("Publico mi nuevo estado %s" + self.state)
                self.mqttc.publish('souliss/%s/%s/state' % (self.device_class, self.name), self.state)
            """

    """
    def publish(self, mqttc):
        if self.mqtt:
            self.mqttc = mqttc
            self.device_class = typical_types[self.ttype]['mqtt']
            mqttc.publish('souliss/%s/%s/config' % (self.device_class, self.name),
                          '{"name" : "' + self.friendly_name + '", ' +
                          '"payload_on": "01", ' +
                          '"payload_off": "00", ' +
                          '"optimistic": false, ' +
                          '"retain": true, ' +
                          '"command_topic": "souliss/%s/%s/set", "state_topic": "souliss/%s/%s/state"}' \
                          % (self.device_class, self.name, self.device_class, self.name))
                         #'{"name" : "once,", "payload_on": "0", "payload_off": "1", "optimistic": false, "retain": true, "state_topic": "souliss/switch/%s", "command_topic": "souliss/switch/%s/set"}' % (self.name, self.name))
            #mqttc.subscribe("souliss/%s/%s/#" % (self.device_class, self.name))
            #mqttc.subscribe("souliss/switch/%s" % self.name)

        else:
            print('WARNING: I do not know mqtt device for ' + self.description)

    """
    def set_node_slot_index(self, node, slot, index):
        self.node = node
        self.slot = slot
        self.index = index

    def to_dict(self):
        return {'ddesc': self.description,
                'slo': self.slot,
                'typ': self.ttype}

class TypicalT1n(Typical):

    def __init__(self, ttype):
        super(TypicalT1n,self).__init__(ttype)
        self.state_desc = typical_types[ttype]['state_desc']

    def update(self, value):
        value = value[:self.size]
        if value != self.state:
            self.state = value
            if self.size > 1: # Raw description for Typicals T15, T16 and T19 
                self.state_description = value
            else:
                self.state_description = self.state_desc[ord(value)]

            _LOGGER.info("Node %d: Typical %d - %s updated to %s" % (self.node, self.index,
                self.description,
                self.state_description))

            for listener in self.listeners:
                listener(self)

    def send_command(self, command):
        # TODO: Handle different T1 behaviour
        if command == 0x01:  # Toggle
            if self.state == chr(1):
                self.update(chr(0))
            else:
                self.update(chr(1))
        elif command == 0x02:  # OnCmd
            self.update(chr(0))
        elif command == 0x04:  # OffCmd
            self.update(chr(1))
        else:
            _LOGGER.debug('Command %x not implemented' % command)

class TypicalT5n(Typical):
    def __init__(self, ttype):
        super(TypicalT5n,self).__init__(ttype)
        self.units= typical_types[ttype]['units']

    def update(self, value):
        value = value[:self.size]
        if value != self.state:
            self.state_description = struct.unpack('e', value)[0]
            self.state = value
            _LOGGER.info("Node %d: Typical %d - %s updated to %s %s" % (self.node, self.index,
                self.description,
                self.state_description,
                self.units))

            for listener in self.listeners:
                listener(self)

class TypicalNotImplemented(Typical):
    def __init__(self, ttype):
        _LOGGER.warning('Typical %x not implemented' % ttype)
        super(TypicalNotImplemented,self).__init__(ttype)

