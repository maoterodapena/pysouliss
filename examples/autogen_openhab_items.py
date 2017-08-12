"""
Example for using pysouliss.
"""

import souliss.pysouliss as souliss
from optparse import OptionParser
import logging

_LOGGER = logging.getLogger(__name__)

dict_openhab = {
    0x11: {'itemtype' : "Switch",
           'itemname' : "Switch_T11",
           'groups': ['Switches'],
           'iconname': 'switch'
           },
    0x12: {'itemtype' : "Switch",
           'itemname' : "Switch_T12",
           'groups': ['Switches'],
           'iconname': 'switch'
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

    # while not SOULISS.all_discovered():
    while SOULISS.nodes_discovered < 1:
        SOULISS.get_response()

    for node in SOULISS.nodes:
        for typical in node.typicals:
            oh_groups = []

            if typical.ttype in dict_openhab.keys():
                oh_itemtype = dict_openhab[typical.ttype]['itemtype']
                oh_itemname = "%s_%d_%d" % (
                    dict_openhab[typical.ttype]['itemname'],
                    node.index,
                    typical.index)
                oh_labeltext = oh_itemname
                oh_iconname = dict_openhab[typical.ttype]['iconname']
                for g in dict_openhab[typical.ttype]['groups']:
                    oh_groups.append(g)
                oh_groups.append("Node_%d" % node.index)
                oh_groups.append("gSouliss")

                oh_binding = "souliss=\"T%s:%d:%d\"" % (hex(typical.ttype)[2:],
                                           node.index,
                                           typical.index)

                line = ("%s %s \"%s\" <%s> (%s) {%s}\n" % (
                    oh_itemtype,
                    oh_itemname,
                    oh_labeltext,
                    oh_iconname,
                    ", ".join(g for g in oh_groups),
                    oh_binding
                ))

                if (options.output_file is not None):
                    output_file.write(line)
                else:
                    print(line)
