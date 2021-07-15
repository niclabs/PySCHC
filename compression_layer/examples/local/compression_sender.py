import socket, binascii, sys

sys.path.insert(0, "../../code")

from SCHC_Compressor import SCHC_Compressor
from SCHC_RuleManager import SCHC_RuleManager
from common import *

IN_PACKET = "demo.txt"

with open("packets/{}".format(IN_PACKET),"r") as pkt_file:
    package = binascii.unhexlify(pkt_file.read())

rm_device = SCHC_RuleManager()
rm_device.add_rule(rule_97)
rm_device.add_rule(rule_98)
rm_device.add_rule(rule_99)

compressor = SCHC_Compressor(rm_device)

schc_packet, padding = compressor.compress(package,"Up")

print('Enviando paquete')
print(binascii.hexlify(schc_packet))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8099))
s.send(schc_packet)
s.close()

print('Enviado')