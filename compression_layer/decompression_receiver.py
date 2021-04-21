import socket, binascii

from SCHC_Decompressor import SCHC_Decompressor
from SCHC_RuleManager import SCHC_RuleManager
from common import *

rm_network = SCHC_RuleManager()
rm_network.add_rule(rule_97)
rm_network.add_rule(rule_98)
rm_network.add_rule(rule_99)

decompressor = SCHC_Decompressor(rm_network)



print("Esperando paquete...")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", 8099))
s.listen()
c,a = s.accept()
schc_packet = c.recv(2048)
c.close()
s.close()

print("Paquete recibido")
print(binascii.hexlify(schc_packet))

ip_packet = decompressor.decompress(schc_packet, "Up")

OUT_PACKET = "demo2.txt"

with open("packets/{}".format(OUT_PACKET),"wb") as pkt_file:
    pkt_file.write(binascii.hexlify(ip_packet))
