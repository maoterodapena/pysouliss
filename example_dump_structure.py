import sys
from Souliss import *

s = Souliss()
s.set_parameters('192.168.2.77',0xA6, 0x37)

if s.is_available():
    print "Souliss gateway connected. IP: %s" % s.gateway_ip
    s.database_structure_request()
    s.dump_structure()
else:
    print "Souliss not available at %s" % s.gateway_ip
