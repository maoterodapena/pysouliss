from struct import pack


class VNet_frame:

    def __init__(self, node_index=0, user_index=0, payload=''):
        if payload == '':
            pass
        else:
            self.length = payload.len() + 6
            # port . always 0x17 (TODO: don't know why)
            self.port = 0x17

            # last number of gateway IP (if netmask = 255.255.255.0)
            self.destino_final = 17*256

            # Obtained from souliss app (why??? don't remember :(
            self.destino_original = 16    # TODO: works with any number!
            self.payload = payload

    def from_data(self, data):

        self.lengthp1 = data[0]
        self.length = data[1]
        self.port = data[2]
        self.destino_final = data[3:5]
        self.destino_original = data[5:7]
        self.payload = data[7:]

    def get_raw(self):

        return pack("!BBBHH%ds" % (self.payload.len()),
                self.length+1, self.length, self.port,
                self.destino_final, self.destino_original,
                self.payload.get_raw())

    def to_str(self):
        return ":".join("{:02x}".format(ord(c)) for c in self.get_raw()) + " : " + self.payload.to_str()
