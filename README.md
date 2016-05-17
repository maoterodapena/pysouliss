# pysouliss

This is a simple python wrapper to communicate with the home automation framework Souliss.

Please, note this is in a very early stage of development. All kinds of suggestions are welcome. At this point, I am just trying to understand the underlaying communication system.

## Usage

1. Create an object Souliss()
2. Set the gateway IP and node index/user index with set_parameters(ip, node_index, user_index). You can obtain this data from the phone app.

## Methods
**database_structure_request()**: query the gateway and populate a list of nodes, with its slots, on the Souliss object.
**dump_structure**: writes a textual description of the nodes found.
