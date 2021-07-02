# PySCHC

Code of SCHC protocol implemented in Python to be loaded on a [PyCOM](https://pycom.io/) device. This were implemented according to [RFC8376](https://datatracker.ietf.org/doc/html/rfc8376), [RFC8724](https://datatracker.ietf.org/doc/html/rfc8724) and [RFC9011](https://datatracker.ietf.org/doc/html/rfc9011).

## Compression

<Anoten lo que necesiten>

## Fragmentation

### On Local computer

#### Installation

1. (Opcional) Create a new virtual environment to install Fragmentation package.

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

2. It is supposed that no package is needed, due to code is going to run on `LoPy`. Server side could have further requirements, but local example simulates Gateway/Node just using sockets.

3. Install `fragmentation_layer` code on virtual environment

   ````bash
   cd fragmentation_layer/code
   
   # As an static package (production)
   python setup.py install 
   
   # As an on-deployment package (develop)
   python setup.py develop 
   
   cd ../..  # To return to root directory on this repo
   ````

#### Execution of example

In two different terminal, one for the receiver and other for the sender.

For the receiver (execute first):

````bash
cd example
python test_receiver.py

# To save logs on a file
python test_receiver.py 2> `<name_of_file>`
````

For the sender (execute in less than [`INACTIVITY_TIMER`](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/code/schc_protocols/lorawan.py) seconds):

````bash
cd example
python test_sender.py

# To save logs on a file
python test_sender.py 2> `<name_of_file>`
````

This will send SCHC Fragments from sender (`localhost:50006`) to receiver (`localhost:50007`) recovering message defined on [`test_sender.py` file](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/example/test_sender.py) and writing it on [`received.txt` text file](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/example/received.txt).

This just use directly the finite machine state of Ack On Error mode of LoRaWAN.

### On LoPy (as Node)

To use on **LoPy** first configure according to PyCOM: [https://docs.pycom.io/gettingstarted/](https://docs.pycom.io/gettingstarted/). To upload the code, use **Pymakr** plugin on [ATOM](https://docs.pycom.io/gettingstarted/software/atom/) or [Visual Studio Code](https://docs.pycom.io/gettingstarted/software/vscode/). And upload all the content of [`fragmentation_layer/code`](https://github.com/niclabs/PySCHC/tree/master/fragmentation_layer/code) folder with a `main.py` file containing message to send and using this API (code below adapted from PyCOM, this use LoRaWAN ABP):

````python
from network import LoRa
import socket
import binascii
import struct

from schc_handlers import SCHCNodeHandler
from schc_protocols import SCHCProtocol

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915)

# create an ABP authentication params
dev_addr = struct.unpack(">l", binascii.unhexlify('your own keys'))[0]
nwk_swkey = binascii.unhexlify('<your own keys>')
app_swkey = binascii.unhexlify('<your own keys>')

# Uncomment for US915 / AU915 & Pygate
for i in range(0, 8):
    lora.remove_channel(i)
for i in range(9, 65):
    lora.remove_channel(i)
for i in range(66, 72):
    lora.remove_channel(i)

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

# Use of this API:
MESSAGE = """
Abstract

   The Static Context Header Compression (SCHC) specification describes
   generic header compression and fragmentation techniques for Low Power
   Wide Area Networks (LPWAN) technologies.  SCHC is a generic mechanism
   designed for great flexibility so that it can be adapted for any of
   the LPWAN technologies.

   This document specifies a profile of RFC8724 to use SCHC in
   LoRaWAN(R) networks, and provides elements such as efficient
   parameterization and modes of operation.

Status of This Memo

   This Internet-Draft is submitted in full conformance with the
   provisions of BCP 78 and BCP 79.

   Internet-Drafts are working documents of the Internet Engineering
   Task Force (IETF).  Note that other groups may also distribute
   working documents as Internet-Drafts.  The list of current Internet-
   Drafts is at https://datatracker.ietf.org/drafts/current/.

   Internet-Drafts are draft documents valid for a maximum of six months
   and may be updated, replaced, or obsoleted by other documents at any
   time.  It is inappropriate to use Internet-Drafts as reference
   material or to cite them other than as "work in progress."

   This Internet-Draft will expire on July 29, 2021.

Copyright Notice

   Copyright (c) 2021 IETF Trust and the persons identified as the
   document authors.  All rights reserved.

   This document is subject to BCP 78 and the IETF Trust's Legal
   Provisions Relating to IETF Documents
   (https://trustee.ietf.org/license-info) in effect on the date of
   publication of this document.  Please review these documents 
   carefully, as they describe your rights and restrictions with respect
   to this document.  Code Components extracted from this document must
   include Simplified BSD License text as described in Section 4.e of
   the Trust Legal Provisions and are provided without warranty as
   described in the Simplified BSD License.
""".encode("ascii")
handler = SCHCNodeHandler(SCHCProtocol.LoRaWAN, mtu=51)
handler.send_package(MESSAGE)
handler.start(s)

````

#### Standard use

To use the methods and class of fragmentation process, import `SCHCNodeHandler` and the protocol you want to use (just LoRaWAN Ack on Error implemented):

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

### On Server

On server side we provide and example using [Flask](https://flask.palletsprojects.com/en/2.0.x/). Install Flask on a virtual environment (see [Installation](https://github.com/niclabs/PySCHC#installation) at the start of this Markdown). And install this API using setup:

````bash
cd fragmentation_layer/code

# As an static package (production)
python setup.py install 

# As an on-deployment package (develop)
python setup.py develop 

cd ../..  # To return to root directory on this repo
````

On the server, use this API as follow:

````python
from flask import request, make_response
import requests
import base64
import json

from schc_handlers.schc_gateway_handler import SCHCGatewayHandler
from schc_protocols import SCHCProtocol

MTU = 51
handler = SCHCGatewayHandler(SCHCProtocol.LoRaWAN, MTU, on_receive_callback=print)
# Parameter on_receive_callback defines the function that is going to be applied
# to the assembled message

def receive_uplink():
    data = request.get_json()
    fport = data["port"]
    dev_id = data["dev_id"]
    downlink_url = data["downlink_url"]
    data = request.get_json()["payload_raw"]
    payload64 = data.encode("ascii")
    msg_bytes = base64.b64decode(payload64)
    handler.handle(msg_bytes, fport, downlink_url, dev_id)
    return json.dumps({"Message": "Okay"}), 200
````

