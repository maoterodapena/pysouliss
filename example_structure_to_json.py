import sys
from Souliss import *

s = Souliss()
s.set_parameters('192.168.2.77',0xA6, 0x37, False) # no loggin

if s.is_available():
    s.database_structure_request()
    s.dump_json_structure()
else:
    print "Souliss not available at %s" % s.gateway_ip
