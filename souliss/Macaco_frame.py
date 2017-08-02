from struct import pack

# List of tested functional codes
MACACO_DESC = {
    0x08: 'Ping',
    0x18: 'Ping answer',
    0x05: 'Subscription request',
    0x15: 'Subscription answer',
    0x26: 'Database structure request',
    0x22: 'Read typical logic request',
    0x32: 'Read typical logic answer',
    0x21: 'Read state request with subscription',
    0x31: 'Read state answer with subscription',
    0x31: 'Read state request with subscription',
    0x33: 'Force imput values'
    }


class Macaco_frame:

    def __init__(self, functional_code=0, put_in=0, start_offset=0, number_of=0, payload=None):
        self.functional_code = functional_code  # 1 byte
        self.put_in = put_in                    # 1 byte
        self.number_of = number_of              # 1 byte
        self.start_offset = start_offset        # 1 byte
        self.payload = payload                  # variable

    @staticmethod
    def from_data(data):
        functional_code = ord(data[0])
        put_in = ord(data[1]) * 256 + ord(data[2])
        start_offset = ord(data[3])
        number_of = ord(data[4])
        payload = data[5:]
        mc = Macaco_frame(functional_code, put_in, start_offset, number_of, payload)
        return mc

    def get_raw(self):
        if self.payload:
            return pack('!BHBB', self.functional_code, 0, 0, self.number_of) + self.payload
        else:
            return pack('!BHBB', self.functional_code, 0, 0, self.number_of)

    def len(self):
        return len(self.get_raw())

    def to_str(self):
        if self.functional_code in MACACO_DESC.keys():
            return MACACO_DESC[self.functional_code]
        else:
            return "Functional code '%s' not found" % "{:02x}".format(self.functional_code)
