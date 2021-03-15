""" test_receiver: Test script Receiver side"""

import socket
import logging
from random import gauss

HOST            = "127.0.0.1"
RECEIVER_PORT   = 50006
SENDER_PORT     = 50007

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, RECEIVER_PORT))
sock.listen(1)

def send_socket(msg: bytes) ->  None:
    sockTx = socket.socket()
    sockTx.connect((HOST, SENDER_PORT))
    sockTx.send(msg)
    sockTx.close()
    return


def receive_socket() -> bytes:
    conn, addr = sock.accept()
    data = conn.recv(1024)
    return data


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from schc_machines.lorawan import UplinkReceiver
    from schc_protocols import LoRaWAN

    receiver = UplinkReceiver(
        LoRaWAN(LoRaWAN.UPLINK)
    )

    while True:
        while True:
            try:
                mtu = int(gauss(20, 2))
                message = receiver.generate_message(mtu)
                logging.info("Current mtu: {}".format(mtu))
                send_socket(b"".join(message.as_bytes()))
            except RuntimeError as e:
                break
        data = receive_socket()
        if data:
            receiver.receive_message(data)
