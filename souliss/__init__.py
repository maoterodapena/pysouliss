"""Python implementation of Souliss API."""
import logging
import socket
import json
from .Typicals import Typical
from .Macaco_frame import Macaco_frame
from .VNet_frame import VNet_frame
import sys
import struct
import time

import random   # just for testing, discarting random response packages

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
SOULISS_FC_READ_TYPICAL_LOGIC_ANSWER = 0x32
SOULISS_FC_FORCE_REQUEST = 0x33
SOULISS_FC_NODES_HEALTHY_REQUEST = 0x25
SOULISS_FC_DATA_REQUEST = 0x27
SOULISS_FC_DISCOVER_GATEWAY_REQUEST = 0x28

# TODO: Dynamic network configuration

class Node:
    # constructor
    def __init__(self, i):
        self.index = i          # index of the typical
        self.typicals = []      # list of typicals 
        self.next_slot = 0      # used internally. When a typical is added to a node,
                                #   next_slot is incremented

    # add a typical to a node previously created
    def add_typical(self, typical):
        self.typicals.append(typical)
        # once a typical belongs to a node, we store node index and slot in it
        typical.set_node_slot_index(self.index, self.next_slot, len(self.typicals)-1)
        self.next_slot = self.next_slot + typical.size

    def to_dict(self):
        return {'ndesc': 'Nodo ' + str(self.index),
                'slot': [t.to_dict() for t in self.typicals]}

class Souliss:

    # constructor
    def __init__(self, gateway_ip, node_index=33, user_index=44):
        self.gateway_ip = gateway_ip
        self.server_address = (gateway_ip, 230)  # default port on souliss
        self.node_index = node_index
        self.user_index = user_index
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(15)

        self.connected = False
        self.typical_update_callback = None
        self.nodes = []
        self.num_nodes = 0

    def is_connected(self):
        return self.connected

    def set_typical_update_callback(self, callback):
        # This callback is called whenever a typical is updated.
        self.typical_update_callback= callback;

    def send(self, functional_code, number_of=0, macaco_payload=None):
        macaco_frame = Macaco_frame(functional_code, 0, 0, number_of, macaco_payload)
        vnet_frame = VNet_frame(self, macaco_frame)

        _LOGGER.debug('sending  -> %s ' % (vnet_frame.to_str()))

        try:
            self.socket.sendto(vnet_frame.get_raw(), self.server_address)
        except:
            _LOGGER.error("Could not connect to souliss gateway. %s" %
                          (sys.exc_info()[1]))
            return False 
        return True

    def subscribe_all_typicals(self):
        for node in range(len(self.nodes)):
            self.send(SOULISS_FC_READ_STATE_REQUEST_WITH_SUBSCRIPTION,
               len(self.nodes[node].typicals))
            time.sleep(0.3)

    def get_response(self, expected_response=None):
        # _LOGGER.info('waiting response... %s' % "{:02x}".format(response_code + RESPONSE))
        try:
            data, server = self.socket.recvfrom(1024)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            return False

        # TODO: Testing. Discard random packages
        # if random.randint(1,10) < 6:
        #    return False
        macaco_frame = Macaco_frame.from_data(data[7:])
        vnet_frame = VNet_frame(self, macaco_frame)
        self.connected = True

        _LOGGER.debug('received <- %s ' % (vnet_frame.to_str()))
        self.process(macaco_frame)

    def process(self, macaco_frame):

        if macaco_frame.functional_code == SOULISS_FC_DATABASE_STRUCTURE_ANSWER:
            self.num_nodes = macaco_frame.payload[0]
            _LOGGER.info("%d nodes found" % self.num_nodes)

            # Re create the nodes
            self.nodes = []
            for n in range(self.num_nodes):
                self.nodes.append(Node(n))

            # Request logic for all nodes
            self.send(SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST, self.num_nodes)

        elif macaco_frame.functional_code == SOULISS_FC_READ_TYPICAL_LOGIC_ANSWER:
            node = macaco_frame.start_offset
            if node > self.num_nodes:
                _LOGGER.debug('Received logic description for node %d, but does not exist! Retrying query database' % node)
                self.send(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)
            elif len(self.nodes[node].typicals) > 0:
                _LOGGER.debug('Duplicate logic description for node %d. Discarting.' % node)
            else:
                mem = 0
                while (mem < macaco_frame.number_of):
                    tipo = macaco_frame.payload[mem]
                    # TODO: Why gateway responds payloads with empty
                    # typicals?
                    if tipo == 0:
                        mem = mem + 1
                        continue
                    if tipo in Typicals.typical_types.keys():
                        new_typical = Typical.factory_type(tipo)
                        if self.typical_update_callback is not None:
                            new_typical.add_listener(self.typical_update_callback)
                        self.nodes[node].add_typical(new_typical)
                        _LOGGER.info('Node %d. Added typical %s: %s' % (node, hex(tipo),Typicals.typical_types[tipo]['desc']))
                        mem = mem + Typicals.typical_types[tipo]['size']
                    else:
                        _LOGGER.warning('Typical ' + hex(tipo) + ' not implemented')

                self.send(SOULISS_FC_READ_STATE_REQUEST_WITH_SUBSCRIPTION, node)

        elif macaco_frame.functional_code == SOULISS_FC_READ_STATE_ANSWER:
            node = macaco_frame.start_offset
            if node >= self.num_nodes:
                _LOGGER.debug('Received state for node %d, but does not exist! Retrying query database' % node)
                self.send(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)
            elif len(self.nodes[node].typicals) == 0:
            # Node still empty. May be READ_TYPICAL_LOGIC_ANSWER was lost
                _LOGGER.debug('Received state for node %d, but does not exist. Retrying' % node)
                self.send(SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST, len(self.nodes))
            else:
                typical_index = 0
                mem = 0
                while typical_index < len(self.nodes[node].typicals):
                    self.nodes[node].typicals[typical_index].update(macaco_frame.payload[mem:])
                    mem = mem + self.nodes[node].typicals[typical_index].size
                    typical_index = typical_index + 1

        else:
            _LOGGER.warning("Functional code not implemented")



    def database_structure_request(self):
        _LOGGER.info('Trying to connect to gateway')
        return self.send(SOULISS_FC_DATABASE_STRUCTURE_REQUEST)

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
