"""
Example for using pysouliss.
"""
import souliss as souliss
from optparse import OptionParser
import logging

_LOGGER = logging.getLogger(__name__)


def set_main_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-g", "--gateway", dest="gateway",
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

    # Try to connect to souliss gateway
    SOULISS = souliss.Souliss(options.gateway)
    ok = SOULISS.database_structure_request()

    if ok:
        SOULISS.subscribe_all_typicals(0)  # subscribe to all typicals on node 0
        while True:
            SOULISS.get_response()
    else:
        print("Terminated")
