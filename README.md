# PySCHC

Code of SCHC protocol implemented in Python to be loaded on a [PyCOM](https://pycom.io/) device.

## Compression Layer

The compression layer has not been tested in LoPy and should be considered unfinished. The following example indicates how to run an example where the sender and the receiver are on the same machine and the message is a IPv6 packet. There is currently no integration with the fragmentation layer.

### Example on local computer

Before running the example, the `pycryptodome` library must be installed.

#### Execution of example

Open two different terminals, one for the receiver and other for the sender.

For the receiver (execute first):

````bash
cd compression_layer/examples/local
python compression_receiver.py
````

For the sender:

````bash
cd compression_layer/examples/local
python compression_sender.py
````

This will send a SCHC Packet from sender to receiver through the socket `localhost:8099`. The IPv6 packet that is sent is in `packets/demo.txt` and after succesfully being decompressed is saved in `packets/demo2.txt`.

### Future work

There are a few main tasks to be adressed before this layer is considered complete:

1. **Create an installation script**: This layer must be installed as a library, similarly to the fragmentation layer.

2. **Refactor Protocol Parser**: Currently, this layer only supports an IPv6 for compression (SCHC_Parser.py) with no easy way to specify other protocols. The protocol selection must be dynamic on library initialization (see protocol selection on fragmentation layer).

3. **Test and adjust LoPy compatibility**: This layer has to run on LoPy alongside the fragmentation layer.

4. **Integration with fragmentation**: compressed packets must be delivered and received from the fragmetation layer. This is likely more direct if done from the fragmentation layer's side.

<make code install like library>
<Not finished, port to be lopy compatible, refactor parser to be selected programatically (like lpwan protocol in fragmentation)>

## Fragmentation Layer

### Example on local computer

The following steps indicate how to run an example where the sender and the receiver are on the same machine and a message is sent with the `ACK-On-Error` mode specified in the LoRaWAN profile. A successful run means the packet fragmentation/reassembly is working as intended.

#### Installation

1. (Optional) Create a new virtual environment to install Fragmentation package.

   Using [`conda`](https://docs.conda.io/en/latest/):

   ````bash
   conda create -n niclabs-schc python=3.9
   
   # Activate
   conda activate niclabs-schc
   ````

   Using [`venv`](https://docs.python.org/3.8/library/venv.html):

   ````bash
   python3 -m venv niclabs-schc
   
   # Activate
   # On Linux and macOS
   source env/bin/activate
   # On Windows
   .\niclabs-schc\env\Scripts\activate
   ````

2. Install `fragmentation_layer` code on virtual environment.

   ````bash
   cd fragmentation_layer/code
   
   # As an static package (production)
   python setup.py install 
   
   # As an on-deployment package (develop)
   python setup.py develop 
   
   cd ../..  # To return to root directory on this repo
   ````

#### Execution of example

Open two different terminals, one for the receiver and other for the sender.

For the receiver (execute first):

````bash
cd fragmentation_layer/examples/local
python test_receiver.py

# To save logs on a file
python test_receiver.py 2> `<name_of_file>`
````

For the sender (execute in less than [`INACTIVITY_TIMER`](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/code/schc_protocols/lorawan.py) seconds):

````bash
cd fragmentation_layer/examples/local
python test_sender.py

# To save logs on a file
python test_sender.py 2> `<name_of_file>`
````

This will send SCHC Fragments from sender (`localhost:50006`) to receiver (`localhost:50007`) recovering the message defined on [`test_sender.py` file](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/example/test_sender.py) and writing it on [`received.txt` text file](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/example/received.txt).

This example only uses the finite state machines of ACK-On-Error mode.


### On LoPy (as Node)

To use this library on **LoPy**, you first need to configure the device according to PyCOM instructions: [https://docs.pycom.io/gettingstarted/](https://docs.pycom.io/gettingstarted/).

#### Installation

1. Create a `main.py` and other required files.

   The `main.py` file is the one that is run by the **LoPy** in order to obtain or create the data to be sent, use the library to fragment it, and send the packets. An example of [`main.py`](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/examples/lopy/main.py) is available in `fragmentation_layer/examples/lopy` alongside a `message.py` file that is imported.

2. Copy all needed files to the device.

   This includes:
   + The contents of `fragmentation_layer/code`.
   + The `main.py` file and other imports.

   The **Pymakr** plugin on [ATOM](https://docs.pycom.io/gettingstarted/software/atom/) or [Visual Studio Code](https://docs.pycom.io/gettingstarted/software/vscode/) can be used for this purpose.

#### Standard use

To use the methods and classes of the fragmentation layer, import `SCHCNodeHandler` and the protocol you want to use (currently only LoRaWAN ACK-On-Error is implemented):

````python
from schc_handlers import SCHCNodeHandler
from schc_protocols import SCHCProtocol

# First parameter of Node is the protocol, in this case LoRaWAN
node = SCHCNodeHandler(SCHCProtocol.LoRaWAN, mtu=51)  # change to use other mtu

# Load the message you want to send
handler.send_package(b"A message")

# Define the socket your hardware use
import socket
s = socket#.methods according to each socket
handler.start(s)
````

### On Server (as Gateway)

To use this library on a server, an HTTP Server listening to and processing The Things Network (TTN) requests is required. A small [Flask](https://flask.palletsprojects.com/en/2.0.x/) server with this functionality is provided in `fragmentation_layer/examples/flask_server`. This Readme does not include an explanation of how to configure a TTN account to connect a device and the server.

#### Installation

1. (Optional) Create a new virtual environment to install Fragmentation package.

   Using [`conda`](https://docs.conda.io/en/latest/):

   ````bash
   conda create -n niclabs-schc python=3.9
   
   # Activate
   conda activate niclabs-schc
   ````

   Using [`venv`](https://docs.python.org/3.8/library/venv.html):

   ````bash
   python3 -m venv niclabs-schc
   
   # Activate
   # On Linux and macOS
   source env/bin/activate
   # On Windows
   .\niclabs-schc\env\Scripts\activate
   ````

2. Install `fragmentation_layer` code on virtual environment.

   ````bash
   cd fragmentation_layer/code
   
   # As an static package (production)
   python setup.py install 
   
   # As an on-deployment package (develop)
   python setup.py develop 
   ````

3. (Optional) Install Flask server.

   Copy files in `fragmentation_layer/examples/flask_server` to a desired location and install the Flask library on the virtual enviroment.

#### Execution of example

On the location of the Flask server:

````python
python app_server.py
````

The server should now be running and waiting for TTN requests to the `/uplink` subdirectory. All reassembled packets will be saved in and overwrite a `received.bin` file.

#### Standard use

On the server, use this API as follows:

````python
from flask import request
import base64
import json

from schc_handlers.schc_gateway_handler import SCHCGatewayHandler
from schc_protocols import SCHCProtocol

# This function is called after the succesful reassembly of a packet
def example_callback(msg):
    print(msg)

MTU = 51

handler = SCHCGatewayHandler(SCHCProtocol.LoRaWAN, MTU, on_receive_callback=example_callback)
# If no callback is given to the handler, reassembled data will be printed on stdout as bytes.

def receive_uplink():
    # Obtaining data from TTN requests
    data = request.get_json()
    downlink_url = request.headers["x-downlink-push"]
    fport = data["uplink_message"]["f_port"]
    dev_id = data["end_device_ids"]["device_id"]
    api_key = request.headers["x-downlink-apikey"]
    data = request.get_json()["uplink_message"]["frm_payload"]
    payload64 = data.encode("ascii")
    msg_bytes = base64.b64decode(payload64)

    # Packet processing
    handler.handle(msg_bytes, fport, downlink_url, dev_id, api_key)
    # This is an example for LoRaWAN. Different protocols may not require all these values
    # Only msg_bytes is required by the method signature.
    return json.dumps({"Message": "Okay"}), 200
````

