MACACO_DESC = {
    0x08: 'Ping',
    0x26: 'Database structure request',
    0x22: 'Read typical logic request'
    }

"""
SOULISS_FC_READ_REQUEST_FOR_DIGITAL_VALUES = 0x01       # TODO
SOULISS_FC_READ_REQUEST_FOR_ANALOG_VALUES = 0x02        # TODO
SOULISS_FC_SUBSCRIPTION_REQUEST = 0x05                  # TODO
SOULISS_FC_FORCE_BACK_REGISTER_VALUE = 0x13             # TODO
SOULISS_FC_FORCE_REGISTER_VALUE = 0x14                  # TODO
SOULISS_FC_FORCE_REGISTER_VALUE_AND = 0x16              # TODO
SOULISS_FC_FORCE_REGISTER_VALUE_OR = 0x17               # TODO

# Gateway FC's
SOULISS_FC_READ_STATE_REQUEST_WITH_SUBSCRIPTION = 0x21  # TODO
SOULISS_FC_READ_TYPICAL_LOGIC_REQUEST = 0x22            # TODO
SOULISS_FC_FORCE_REQUEST = 0x33                         # TODO
SOULISS_FC_NODES_HEALTHY_REQUEST = 0x25                 # TODO
SOULISS_FC_DATA_REQUEST = 0x27                          # TODO
SOULISS_FC_DISCOVER_GATEWAY_REQUEST = 0x28              # TODO
"""

class Macaco_frame:


    def __init__(self, functional_code, number_of=0):
        self.functional_code=functional_code;
        self.number_of = number_of

    def from_data(self, data):
        self.functional_code = data[0]
        self.put_in = data[1:2]
        self.start_offset = data[3]
        self.number_of = data[4]
        self.payload = data[5:]
        
    def get_raw(self):
        """
            0,0,        #/ putin 
            0,          #/ star offset
            0])          # number of
        """
        return chr(self.functional_code) + "\x00\x00\x00" + chr(self.number_of)

    def len(self):
        return 5;

    def to_str(self):
        if self.functional_code in MACACO_DESC.keys():
            return MACACO_DESC[self.functional_code]
        elif self.functional_code + 0x10 in MACACO_DESC.keys():
            return MACACO_DESC[self.functional_code] + " response"
        else:
            return "Functional code '%s' not found" % "{:02x}".format(self.functional_code)




