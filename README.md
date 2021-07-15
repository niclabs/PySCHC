# PySCHC

Code of SCHC protocol implemented in Python to be loaded on a [PyCOM](https://pycom.io/) device.

## Compression

<Anoten lo que necesiten>

## Fragmentation Layer

### Example on local computer

The following steps indicate how to run an example where the sender and the receiver are on the same machine and a message is sent with the `ACK-On-Error` mode specified in the LoRaWAN profile. A successful run means everything is working as intended.

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

2. Install `fragmentation_layer` code on virtual environment

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
cd examples/local
python test_receiver.py

# To save logs on a file
python test_receiver.py 2> `<name_of_file>`
````

For the sender (execute in less than [`INACTIVITY_TIMER`](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/code/schc_protocols/lorawan.py) seconds):

````bash
cd examples/local
python test_sender.py

# To save logs on a file
python test_sender.py 2> `<name_of_file>`
````

This will send SCHC Fragments from sender (`localhost:50006`) to receiver (`localhost:50007`) recovering message defined on [`test_sender.py` file](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/example/test_sender.py) and writing it on [`received.txt` text file](https://github.com/niclabs/PySCHC/blob/master/fragmentation_layer/example/received.txt).

### On LoPy as Node

<Al toque Bodeque>

### On LoPy as Gateway

<Al toque Bodeque>

