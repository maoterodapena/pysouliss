# pysouliss
Python API for talking to a Souliss gateway (http://souliss.net/). This is a very early stage of the project.

# Demo
After cloning the repository you can test it with your actual configuration with:
```
python main.py -v -g <ip-gateway>
```

# Usage
```python
import souliss.souliss as souliss
SOULISS = souliss.Souliss('192.168.1.77')
ok = SOULISS.database_structure_request()

if ok:
    SOULISS.subscribe_all_typicals(0) # subscribe to all typicals on node 0
    while True:
        SOULISS.get_response()
```

In the above example PySouliss will get the nodes and typicals on the gateway and start listening to events on node 0, keeping an internal state of each typical and showing a messagge if something changes.

