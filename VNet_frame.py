class VNet_frame:

    def __init__(self, node_index, user_index, payload):
        self.length = payload.len() + 6
        # port . always 0x17 (TODO: don't know why)
        self.port = chr(0x17)

        # last number of gateway IP (if netmask = 255.255.255.0)
        self.destino_final = chr(0x4d) + chr(0)

        # Obtained from souliss app
        self.destino_original = chr(node_index) + chr(user_index)
        self.payload = payload

    def get_raw(self):

        return chr(self.length + 1) + chr(self.length) + self.port + self.destino_final + self.destino_original + self.payload.get_raw()

    def to_str(self):
        return ":".join("{:02x}".format(ord(c)) for c in self.get_raw())


