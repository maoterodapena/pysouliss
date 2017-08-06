"""Python implementation of Souliss API."""
import logging
import socket
import json
from .Typicals import Typical
from .Macaco_frame import Macaco_frame
from .VNet_frame import VNet_frame
import sys
import struct

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
        vnet_frame = VNet_frame(self, macaco_frame)

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

        vnet_frame = VNet_frame(self, macaco_frame)
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
                        if tipo in Typicals.typical_types.keys():
                            new_node.add_typical(Typical.factory_type(tipo))
                            _LOGGER.info('Added typical ' + hex(tipo) + ':' +
                                         Typicals.typical_types[tipo]['desc'])
                            mem = mem + Typicals.typical_types[tipo]['size']
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
