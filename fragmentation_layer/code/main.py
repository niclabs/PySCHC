from network import LoRa
import socket
import binascii
import struct

from message import MESSAGE
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
dev_addr = struct.unpack(">l", binascii.unhexlify('26011011'))[0]
nwk_swkey = binascii.unhexlify('40792D626980A95B0F1F863C291D420E')
app_swkey = binascii.unhexlify('5ED101DD805B089C90BC3BD1061EA6FC')

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

handler = SCHCNodeHandler(SCHCProtocol.LoRaWAN, 51)
handler.send_package(MESSAGE)
handler.start(s)
