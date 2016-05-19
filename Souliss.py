from socket import *
from Macaco_frame import Macaco_frame
from VNet_frame import VNet_frame

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

typical = {
    0x11:"ON/OFF Salida digital con timer",
    0x12:"ON/OFF Salida con modo AUT",
    0x13:"Valor de entrada digital",
    0x14:"Pulso de salida digital",
    0x16:"Tira de LED RGB",
    0x18:"ON/OFF Salida Digital",
    0x19:"Luz Regulable",
    0x19:"Brillo actual:",
    0x19:"Configurar brillo a:",
    0x21:"Dispositivo motorizado (con final de carrera)",
    0x22:"Dispositivo motorizado",
    0x31:"Termostato",
    0x41:"Sistema antirobo",
    0x42:"Peer antirobo",
    0x51:"Entrada analogica",
    0x52:"Entrada analogica, valor medio",
    0x53:"Entrada analogica, interactividad maxima",
    0x54:"Sensor de luz",
    0x55:"Sensor de Voltaje",
    0x56:"Sensor de Corriente",
    0x57:"Sensor de Potencia",
    0x58:"Sensor de Presion",
    0x61:"Analog setpoint, half-precision floating point",
    0x62:"Temperature setpoint (-20, +50)C",
    0x63:"Humidity setpoint (0, 100)%",
    0x64:"Light setpoint (0, 40) kLux",
    0x65:"Voltage setpoint(0, 400) V",
    0x66:"Current setpoint(0, 25) A",
    0x67:"Power setpoint(0, 6500) W",
    0x68:"Pressure setpoint (0, 1500) hPa"
    }

class Typical:
    def __init__(self, type):
        self.type = type
        self.description = typical[type]
        
class Node:
    def __init__(self, i):
        self.index = i
        self.typicals = []
        pass

    def add_typical(self, typical):
        self.typicals.append(typical)

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
        if self.log:
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
                        if tipo>0:
                            new_node.add_typical(Typical(tipo))
                self.nodes.append(new_node)
        self.log ('database_structure_request OK')
        
    def dump_structure(self):
        for n in self.nodes:
            print "Nodo %d de %d" % (n.index+1, len(self.nodes))
            for t in n.typicals:
                print "   Tipo: %d - %s" % (t.type, t.description)

    def close(self):
        self.socket.close()

