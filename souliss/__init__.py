"""Python implementation of Souliss API."""
import logging
import socket
import json
from .Macaco_frame import Macaco_frame
from .VNet_frame import VNet_frame
import sys

_LOGGER = logging.getLogger(__name__)

RESPONSE = 0x10

SOULISS_FC_READ_REQUEST_FOR_DIGITAL_VALUES = 0x01       # TODO
SOULISS_FC_READ_REQUEST_FOR_ANALOG_VALUES = 0x02        # TODO
SOULISS_FC_SUBSCRIPTION_REQUEST = 0x05                  # TODO
SOULISS_FC_SUBSCRIPTION_ANSWER = 0x15                   # TODO
SOULISS_FC_FORCE_BACK_REGISTER_VALUE = 0x13             # TODO
SOULISS_FC_FORCE_REGISTER_VALUE = 0x14                  # TODO
SOULISS_FC_FORCE_REGISTER_VALUE_AND = 0x16              # TODO
SOULISS_FC_FORCE_REGISTER_VALUE_OR = 0x17               # TODO
SOULISS_FC_PING = 0x08

# Gateway FC's
SOULISS_FC_DATABASE_STRUCTURE_REQUEST = 0x26
SOULISS_FC_DATABASE_STRUCTURE_ANSWER = 0x36
SOULISS_FC_READ_STATE_REQUEST_WITH_SUBSCRIPTION = 0x21
SOULISS_FC_READ_STATE_ANSWER = 0x31
SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST = 0x22
SOULISS_FC_FORCE_REQUEST = 0x33
SOULISS_FC_NODES_HEALTHY_REQUEST = 0x25
SOULISS_FC_DATA_REQUEST = 0x27
SOULISS_FC_DISCOVER_GATEWAY_REQUEST = 0x28

# TODO: Dynamic network configuration

typical_types = {
        0x11: {
            "desc": "Typical 11 : ON/OFF Digital Output with Timer Option", "size": 1,
        },
        0x12: {"desc": "Typical 12 : ON/OFF Digital Output with AUTO mode", "size": 1},
        0x13: {"desc": "Typical 13 : Digital Input Value", "size": 1},
        0x14: {"desc": "Typical 14 : Pulse Digital Output", "size": 1},
        0x15: {"desc": "Typical 15 : RGB Light", "size": 2},
        0x16: {"desc": "Typical 16 : RGB LED Strip", "size": 4},
        0x18: {"desc": "Typical 18 : ON/OFF Digital Output (Step Relay)", "size": 1},
        0x19: {"desc": "Typical 19 : Single Color LED Strip", "size": 2},
        0x1A: {"desc": "Typical 1A : Digital Input Pass Through", "size": 1},
        0x1B: {"desc": "Typical 1B : Position Constrained ON/OFF Digital Output", "size": 1},
        0x21: {"desc": "Typical 21 : Motorized devices with limit switches", "size": 1},
        0x22: {"desc": "Typical 22 : Motorized devices with limit switches and middle position", "size": 1},
        0x31: {"desc": "Typical 31 : Temperature control with cooling and heating mode", "size": 5},
        0x32: {"desc": "Typical 32 : Air Conditioner", "size": 2},
        0x41: {"desc": "Typical 41 : Anti-theft integration -Main-",  "size": 1},
        0x42: {"desc": "Typical 42 : Anti-theft integration -Peer-",  "size": 1},
        0x51: {"desc": "Typical 51 : Analog input, half-precision floating point", "size": 2},
        0x52: {"desc": "Typical 52 : Temperature measure (-20, +50) C", "size": 2},
        0x53: {"desc": "Typical 53 : Humidity measure (0, 100) ", "size": 2},
        0x54: {"desc": "Typical 54 : Light Sensor (0, 40) kLux", "size": 2},
        0x55: {"desc": "Typical 55 : Voltage (0, 400) V", "size": 2},
        0x56: {"desc": "Typical 56 : Current (0, 25) A", "size": 2},
        0x57: {"desc": "Typical 57 : Power (0, 6500) W", "size": 2},
        0x58: {"desc": "Typical 58 : Pressure measure (0, 1500) hPa", "size": 2},
        0x61: {"desc": "Typical 61 : Analog setpoint, half-precision floating point", "size": 2},
        0x62: {"desc": "Typical 62 : Temperature measure (-20, +50) C", "size": 2},
        0x63: {"desc": "Typical 63 : Humidity measure (0, 100) ", "size": 2},
        0x64: {"desc": "Typical 64 : Light Sensor (0, 40) kLux", "size": 2},
        0x65: {"desc": "Typical 65 : Voltage (0, 400) V", "size": 2},
        0x66: {"desc": "Typical 66 : Current (0, 25) A", "size": 2},
        0x67: {"desc": "Typical 67 : Power (0, 6500) W", "size": 2},
        0x68: {"desc": "Typical 68 : Pressure measure (0, 1500) hPa", "size": 2}
        }

class Typical(object):
    def __init__(self, ttype):
        self.ttype = ttype
        self.description = typical_types[ttype]['desc']
        self.size = typical_types[ttype]['size']
        self.slot = -1  # undefined until assigned to a slot

        # inital state. It will be overwritten with the first update
        self.state = b'\x00\x00\x00\x00\x00\x00\x00'
        self.listeners = []

    def add_listener(self, callback):
        self.listeners.append(callback)

    @staticmethod
    def factory_type(ttype):
        if ttype in [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x18, 0x19, 0x1A, 0x1B]:
            return TypicalT1n(ttype)
        elif ttype in [0x51, 0x522, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58]:
            return TypicalT5n(ttype)
        else:
            return TypicalNotImplemented(ttype)

    def update(self, value):
        value = value[:self.size]
        if value != self.state:
            _LOGGER.info("%d - %s updated from %s to %s" % (self.index,
                self.description,
                ':'.join("{:02x}".format(c) for c in self.state[:self.size]),
                ':'.join("{:02x}".format(c) for c in value[:self.size])))
            self.state = value

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
    def set_slot_index(self, slot, index):
        self.slot = slot
        self.index = index

    def to_dict(self):
        return {'ddesc': self.description,
                'slo': self.slot,
                'typ': self.ttype}

class TypicalT1n(Typical):

    def __init__(self, ttype):
        super(TypicalT1n,self).__init__(ttype)

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

class TypicalNotImplemented(Typical):
    def __init__(self, ttype):
        _LOGGER.warning('Typical %x not implemented' % ttype)
        super(TypicalNotImplemented,self).__init__(ttype)


class Node:
    def __init__(self, i):
        self.index = i
        self.typicals = []
        self.next_slot = 0
        pass

    def add_typical(self, typical):
        if typical is not None:
            typical.set_slot_index(self.next_slot, len(self.typicals))
            self.typicals.append(typical)
        self.next_slot = self.next_slot + typical.size

    def to_dict(self):
        return {'ndesc': 'Nodo ' + str(self.index),
                'slot': [t.to_dict() for t in self.typicals]}


class Souliss:
    # pylint: disable=too-many-instance-attributes

    def __init__(self, gateway_ip, node_index=33, user_index=44):
        self.gateway_ip = gateway_ip
        self.server_address = (gateway_ip, 230)
        self.node_index = node_index
        self.user_index = user_index
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5)

        self.available = False
        self.nodes = []

    def is_available(self):
        self.send(SOULISS_FC_PING)
        return self.get_response() != False

    def send(self, functional_code, number_of=0, macaco_payload=None):
        macaco_frame = Macaco_frame(functional_code, 0, 0, number_of, macaco_payload)
        vnet_frame = VNet_frame(self.node_index, self.user_index, macaco_frame)

        _LOGGER.debug('sending  -> %s ' % (vnet_frame.to_str()))

        self.socket.sendto(vnet_frame.get_raw(), self.server_address)
        return vnet_frame.get_raw()

    def subscribe_all_typicals(self, node):
        self.send(SOULISS_FC_READ_STATE_REQUEST_WITH_SUBSCRIPTION,
               len(self.nodes[node].typicals))

    def get_response(self, expected_response=None):
        # _LOGGER.info('waiting response... %s' % "{:02x}".format(response_code + RESPONSE))
        try:
            if expected_response is None:
                self.socket.settimeout(5)
            else:
                self.socket.settimeout(5)

            data, server = self.socket.recvfrom(1024)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            return False

        macaco_frame = Macaco_frame.from_data(data[7:])

        vnet_frame = VNet_frame(self.node_index, self.user_index, macaco_frame)
        # TODO - no se ve la cabecera vnet
        _LOGGER.debug('received <- %s ' % (vnet_frame.to_str()))

        if macaco_frame.functional_code == SOULISS_FC_READ_STATE_ANSWER:
            mem = macaco_frame.start_offset
            typical_index = 0
            while typical_index < len(self.nodes[0].typicals):
                # print("Hasta: %d Typical index %d - Mem = %d" % (len(self.nodes[0].typicals), typical_index, mem))
                self.nodes[0].typicals[typical_index].update(macaco_frame.payload[mem:])
                mem = mem + self.nodes[0].typicals[typical_index].size
                typical_index = typical_index + 1

        return data

    def database_structure_request(self):
        _LOGGER.info('Trying to connect to gateway')
        self.send(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)
        res = self.get_response(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)
        # _LOGGER.info(Macaco_frame.decode(res))

        if res:
            num_nodes = res[12]
            _LOGGER.info("%d nodes found" % num_nodes)

            for n in range(num_nodes):
                new_node = Node(n)
                self.send(SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST, num_nodes)
                res = self.get_response(SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST)
                if res:
                    size_payload = res[11]
                    mem = 0
                    while (mem < size_payload):
                        # print("itero: %d. Mem = %d" % (size_payload, mem))
                        tipo = res[12+mem]
                        # TODO: Why gateway responds payloads with empty
                        # typicals?
                        if tipo == 0:
                            mem = mem + 1
                            continue
                        if tipo in typical_types.keys():
                            new_node.add_typical(Typical.factory_type(tipo))
                            _LOGGER.info('Added typical ' + hex(tipo) + ':' +
                                         typical_types[tipo]['desc'])
                            mem = mem + typical_types[tipo]['size']
                        else:
                            _LOGGER.error('Typical ' + hex(tipo) + ' not implemented')


                self.nodes.append(new_node)
            _LOGGER.info('database_structure_request OK')
            return True
        else:
            _LOGGER.error('No response for database_structure_request ')
            return False

    # Send command to node/typical
    def send_command(self, command, node_num, typical_num):

        # sanitize parameters
        if type(node_num) is str:
            node_num = int(node_num)
        if type(typical_num) is str:
            typical_num = int(typical_num)

        _LOGGER.debug('Sending %02x to node %d - typical %d', command, node_num, typical_num)
        self.send(SOULISS_FC_FORCE_REQUEST, 1, command)

    def dump_structure(self):
        for n in self.nodes:
            print("Nodo %d de %d" % (n.index+1, len(self.nodes)))
            for t in n.typicals:
                print("   Tipo: %d - %s" % (t.ttype, t.description))

    def dump_json_structure(self):
        res = {'id': []}
        for n in self.nodes:
            res['id'].append(n.to_dict())
        print(json.dumps(res, indent=4))

    def is_open(self):
        return self.socket is not None

    def close(self):
        self.socket.close()
        self.socket = None
