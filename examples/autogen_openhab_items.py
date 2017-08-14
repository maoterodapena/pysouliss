"""
Example for using pysouliss.
"""

import souliss.pysouliss as souliss
from optparse import OptionParser
import logging

_LOGGER = logging.getLogger(__name__)

dict_openhab = {
    0x11: {'itemtype' : "Switch",
           'itemname' : "switch_T11",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x12: {'itemtype' : "Switch",
           'itemname' : "switch_T12",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x13: {'itemtype' : "Switch",
           'itemname' : "switch_T13",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x14: {'itemtype' : "Switch",
           'itemname' : "switch_T14",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x18: {'itemtype' : "Switch",
           'itemname' : "switch_T18",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x1A: {'itemtype' : "Switch",
           'itemname' : "switch_T1A",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x1B: {'itemtype' : "Switch",
           'itemname' : "switch_T1B",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x51: {'itemtype' : "Number",
           'itemname' : "number",
           'labeltext' : "Measure [%.1f units]",
           'groups': ['Measures'],
           'iconname': 'line'
           },
    0x52: {'itemtype' : "Number",
           'itemname' : "temperature",
           'labeltext' : "Temperature [%.1f °C]",
           'groups': ['Temperature', 'Measures'],
           'iconname': 'temperature'
           },
    0x53: {'itemtype' : "Number",
           'itemname' : "humidity",
           'labeltext' : "Humidity [%.1f]",
           'groups': ['Temperature', 'Measures'],
           'iconname': 'humidity'
           },
    0x54: {'itemtype' : "Number",
           'itemname' : "lightsensor",
           'labeltext' : "Light sensor [%.1f] lux",
           'groups': ['Measures'],
           'iconname': 'line'
           },
    0x55: {'itemtype' : "Number",
           'itemname' : "voltage",
           'labeltext' : "Voltage [%.1f] V",
           'groups': ['Measures'],
           'iconname': 'line'
           },
    0x56: {'itemtype' : "Number",
           'itemname' : "current",
           'labeltext' : "Current [%.1f] A",
           'groups': ['Measures'],
           'iconname': 'line'
           },
    0x57: {'itemtype' : "Number",
           'itemname' : "power",
           'labeltext' : "Power [%.1f] W",
           'groups': ['Measures'],
           'iconname': 'line'
           },
    0x58: {'itemtype' : "Number",
           'itemname' : "pressure",
           'labeltext' : "Pressure [%.1f] W",
           'groups': ['Measures'],
           'iconname': 'pressure'
           }

}


def set_main_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-g", "--gateway", dest="gateway",
                      help="Souliss gateway host or IP")
    parser.add_option("-o", "--output_file", dest="output_file",
                      help="Souliss gateway host or IP")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")

    (options, args) = parser.parse_args()
    if options.gateway is None:
        parser.error("You need to provide a gateway host or IP")

    if options.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    return options

if __name__ == "__main__":

    # Parse command line options
    options = set_main_options()

    if (options.output_file is not None):
        output_file = open(options.output_file, 'w')

    # Try to connect to souliss gateway
    SOULISS = souliss.Souliss(options.gateway)
    SOULISS.database_structure_request()

    # Wait until all nodes are discovered
    while not SOULISS.all_discovered():
        SOULISS.get_response()

    output_text = ""

    # Output a "Souliss group"
    output_text = "Group gSouliss      \"Souliss\"       <sun>\n"

    for node in SOULISS.nodes:
        output_text = output_text + "Group Node_%d \"Node %d\"     <sun> (gSouliss)\n" % (
            node.index, node.index)

        for typical in node.typicals:
            oh_groups = []

            # Is implemented in this program??
            if typical.ttype in dict_openhab.keys():
                oh_itemtype = dict_openhab[typical.ttype]['itemtype']
                oh_itemname = "%s_%d_%d" % (
                    dict_openhab[typical.ttype]['itemname'],
                    node.index,
                    typical.index)
                if 'labeltext' in dict_openhab[typical.ttype]:
                    oh_labeltext = "%s_%d_%d" % (
                        dict_openhab[typical.ttype]['labeltext'],
                        node.index,
                        typical.index)
                else:
                    oh_labeltext = oh_itemname

                oh_iconname = dict_openhab[typical.ttype]['iconname']
                for g in dict_openhab[typical.ttype]['groups']:
                    oh_groups.append(g)
                oh_groups.append("Node_%d" % node.index)
                # oh_groups.append("gSouliss")

                oh_binding = "souliss=\"T%s:%d:%d\"" % (hex(typical.ttype)[2:],
                                           node.index,
                                           typical.slot)

                line = ("%s %s \"%s\" <%s> (%s) {%s}\n" % (
                    oh_itemtype,
                    oh_itemname,
                    oh_labeltext,
                    oh_iconname,
                    ", ".join(g for g in oh_groups),
                    oh_binding
                ))

                output_text = output_text + line
            else:
                print("Typical %s not implemented yet!" % hex(typical.ttype))


    if (options.output_file is not None):
        output_file.write(output_text)
    else:
        print(output_text)
