from socket import *
from Macaco_frame import Macaco_frame
from VNet_frame import VNet_frame
import json

RESPONSE = 0x10

SOULISS_FC_READ_REQUEST_FOR_DIGITAL_VALUES = 0x01       # TODO
SOULISS_FC_READ_REQUEST_FOR_ANALOG_VALUES = 0x02        # TODO
SOULISS_FC_SUBSCRIPTION_REQUEST = 0x05                  # TODO
SOULISS_FC_FORCE_BACK_REGISTER_VALUE = 0x13             # TODO
SOULISS_FC_FORCE_REGISTER_VALUE = 0x14                  # TODO
SOULISS_FC_FORCE_REGISTER_VALUE_AND = 0x16              # TODO
SOULISS_FC_FORCE_REGISTER_VALUE_OR = 0x17               # TODO
SOULISS_FC_PING = 0x08                                  

# Gateway FC's
SOULISS_FC_READ_STATE_REQUEST_WITH_SUBSCRIPTION = 0x21  # TODO
SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST = 0x22            # TODO
SOULISS_FC_FORCE_REQUEST = 0x33                         # TODO
SOULISS_FC_NODES_HEALTHY_REQUEST = 0x25                 # TODO
SOULISS_FC_DATABASE_STRUCTURE_REQUEST = 0x26            # TODO
SOULISS_FC_DATA_REQUEST = 0x27                          # TODO
SOULISS_FC_DISCOVER_GATEWAY_REQUEST = 0x28              # TODO

# TODO: Dynamic network configuration

typical_types = {
        0x11: {"desc" : "Typical 11 : ON/OFF Digital Output with Timer Option", "size": 1},
        0x12: {"desc" : "Typical 12 : ON/OFF Digital Output with AUTO mode", "size": 1},
        0x13: {"desc" : "Typical 13 : Digital Input Value", "size": 1},
        0x14: {"desc" : "Typical 14 : Pulse Digital Output", "size": 1},
        0x15: {"desc" : "Typical 15 : RGB Light", "size": 2},
        0x16: {"desc" : "Typical 16 : RGB LED Strip", "size": 4},
        0x18: {"desc" : "Typical 18 : ON/OFF Digital Output (Step Relay)", "size": 1},
        0x19: {"desc" : "Typical 19 : Single Color LED Strip", "size": 2},
        0x1A: {"desc" : "Typical 1A : Digital Input Pass Through", "size": 1},
        0x1B: {"desc" : "Typical 1B : Position Constrained ON/OFF Digital Output", "size": 1},
        0x21: {"desc" : "Typical 21 : Motorized devices with limit switches", "size": 1},
        0x22: {"desc" : "Typical 22 : Motorized devices with limit switches and middle position", "size": 1},
        0x31: {"desc" : "Typical 31 : Temperature control with cooling and heating mode", "size": 5},
        0x32: {"desc" : "Typical 32 : Air Conditioner", "size": 2},
        0x41: {"desc" : "Typical 41 : Anti-theft integration -Main-",  "size": 1},
        0x42: {"desc" : "Typical 42 : Anti-theft integration -Peer-",  "size": 1},
        0x51: {"desc" : "Typical 51 : Analog input, half-precision floating point", "size": 2},
        0x52: {"desc" : "Typical 52 : Temperature measure (-20, +50) C", "size": 2},
        0x53: {"desc" : "Typical 53 : Humidity measure (0, 100) " , "size": 2},
        0x54: {"desc" : "Typical 54 : Light Sensor (0, 40) kLux", "size": 2},
        0x55: {"desc" : "Typical 55 : Voltage (0, 400) V", "size": 2},
        0x56: {"desc" : "Typical 56 : Current (0, 25) A", "size": 2},
        0x57: {"desc" : "Typical 57 : Power (0, 6500) W", "size": 2},
        0x58: {"desc" : "Typical 58 : Pressure measure (0, 1500) hPa", "size": 2},
        0x61: {"desc" : "Typical 61 : Analog setpoint, half-precision floating point", "size": 2},
        0x62: {"desc" : "Typical 62 : Temperature measure (-20, +50) C", "size": 2},
        0x63: {"desc" : "Typical 63 : Humidity measure (0, 100) ", "size": 2},
        0x64: {"desc" : "Typical 64 : Light Sensor (0, 40) kLux", "size": 2},
        0x65: {"desc" : "Typical 65 : Voltage (0, 400) V", "size": 2},
        0x66: {"desc" : "Typical 66 : Current (0, 25) A", "size": 2},
        0x67: {"desc" : "Typical 67 : Power (0, 6500) W", "size": 2},
        0x68: {"desc" : "Typical 68 : Pressure measure (0, 1500) hPa", "size": 2}
        }


class Typical:
    def __init__(self, ttype):
        self.ttype = ttype
        self.description = typical_types[ttype]['desc']
        self.size = typical_types[ttype]['size']
        self.slot = -1 # undefined until added to a node

    def set_slot(self, slot):
        self.slot = slot

    def to_dict(self):
        return {'ddesc': self.description,
                'slo': self.slot,
                'typ': self.ttype}

        
class Node:
    def __init__(self, i):
        self.index = i
        self.typicals = []
        self.next_slot = 0
        pass

    def add_typical(self, typical):
        typical.set_slot(self.next_slot)
        self.typicals.append(typical)
        self.next_slot = self.next_slot + typical.size

    def to_dict(self):
        return {'ndesc': 'Nodo ' + str(self.index),
                'slot': [t.to_dict() for t in self.typicals]}


class Souliss:


    def __init__(self):
        self.available = False

        self.nodes = []

    def set_parameters(self, ip, node_index, user_index, logging=True):

        self.gateway_ip = ip
        self.server_address = (ip, 230)
        self.node_index = node_index
        self.user_index = user_index
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.settimeout(1)
        self.logging = logging

    def is_available(self):
        self.send(SOULISS_FC_PING)
        return self.get_response(SOULISS_FC_PING) != False

    def log(self, msg):
        if self.logging:
            print "LOG: %s" % msg

    """
    # TODO: This does not work.
    def discover_gateway(self):
        self.log("> Discover gateway")
        functional_code = SOULISS_FC_DISCOVER_GATEWAY_REQUEST
        number_of = 0

        macaco_frame = Macaco_frame(functional_code, number_of)
        message = VNet_frame(self.node_index, self.user_index, macaco_frame).get_raw()

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.log('sending "%s"' % ':'.join("{:02x}".format(ord(c)) for c in message))
        self.socket.sendto(message, ('192.168.2.255',230))

        res = self.get_response(SOULISS_FC_DISCOVER_GATEWAY_REQUEST)
    """


    def send(self, functional_code, number_of=0):
        macaco_frame = Macaco_frame(functional_code, number_of)
        vnet_frame = VNet_frame(self.node_index, self.user_index, macaco_frame)

        self.log('sending "%s" "%s" ' % (vnet_frame.to_str(), macaco_frame.to_str()))

        sent = self.socket.sendto(vnet_frame.get_raw(), self.server_address)

    def get_response(self, response_code):
        self.log('waiting response... %s' % "{:02x}".format(response_code + RESPONSE))
        try:
            data, server = self.socket.recvfrom(1024)
        except:
            self.log('Timeout')
            return False

        self.log('received "%s"' % ':'.join("{:02x}".format(ord(c)) for c in data))
        return data


    def database_structure_request(self):
        self.log ('database_structure_request OK')
        self.send(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)
        res = self.get_response(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)
        self.log(Macaco_frame.decode(res))

        if res:
            num_nodes = ord(res[12])
            self.log ("%d nodes found" % num_nodes)

            for n in xrange(num_nodes):
                new_node = Node(n)
                self.send(SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST, num_nodes)
                res = self.get_response(SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST)
                if res:
                    num_typicals = ord(res[11])
                    for t in xrange(num_typicals):
                        tipo = ord(res[12+t])
                        if tipo>0 and tipo<255:
                            new_node.add_typical(Typical(tipo))
                self.nodes.append(new_node)
        self.log ('database_structure_request OK')
        
    def dump_structure(self):
        for n in self.nodes:
            print "Nodo %d de %d" % (n.index+1, len(self.nodes))
            for t in n.typicals:
                print "   Tipo: %d - %s" % (t.ttype, t.description)
        
    def dump_json_structure(self):
        res = {'id': []}
        for n in self.nodes:
            res['id'].append(n.to_dict())
        print json.dumps(res, indent=4)

    def close(self):
        self.socket.close()

