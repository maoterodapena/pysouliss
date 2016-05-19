from struct import *

class VNet_frame:

    def __init__(self, node_index, user_index, payload):
        self.length = payload.len() + 6
        # port . always 0x17 (TODO: don't know why)
        self.port = 0x17

        # last number of gateway IP (if netmask = 255.255.255.0)
        self.destino_final = 77*256

        # Obtained from souliss app (why??? don't remember :(
        #self.destino_original = node_index*256 + user_index+9
        self.destino_original = 22    # TODO: works with any number!
        self.payload = payload

    def get_raw(self):

        return pack("!BBBHH%ds" % (self.payload.len()),
                self.length+1, self.length, self.port, 
                self.destino_final, self.destino_original, 
                self.payload.get_raw())

    def to_str(self):
        return ":".join("{:02x}".format(ord(c)) for c in self.get_raw())


