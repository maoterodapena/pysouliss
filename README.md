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
SOULISS.database_structure_request()

while True:
    SOULISS.get_response()
```

In the above example PySouliss will get the nodes and typicals on the gateway and start listening to events, keeping an internal state of each typical and showing a messagge if something changes.

