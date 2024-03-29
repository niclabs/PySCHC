""" test_receiver: Test script Receiver side"""

import logging
import socket
from common_methods import messaging_loop, HOST

RECEIVER_PORT = 50006
SENDER_PORT = 50007

socket_rx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_rx.bind((HOST, RECEIVER_PORT))
socket_rx.listen(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from schc_machines.lorawan import AckOnErrorReceiver
    from schc_protocols import LoRaWAN

    receiver = AckOnErrorReceiver(
        LoRaWAN(LoRaWAN.ACK_ON_ERROR)
    )

    messaging_loop(receiver, socket_rx, SENDER_PORT)

    packet = receiver.payload.as_bits()
    residue = packet[0:7]
    packet = packet[7:-1]
    assert len(packet) % 8 == 0

    from schc_base import SCHCObject
    message = SCHCObject.bits_2_bytes(packet)
    with open("received.txt", "w", encoding="utf-8") as received_file:
        received_file.write(message.decode("ascii"))
        received_file.write("\nAnd residue:\t{}\n".format(residue))
