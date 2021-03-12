""" test_receiver: Test script Receiver side"""

import socket
import logging
from random import gauss

HOST = "127.0.0.1"
PORT = 50007


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from schc_machines.lorawan import UplinkReceiver
    from schc_protocols import LoRaWAN

    receiver = UplinkReceiver(
        LoRaWAN(LoRaWAN.UPLINK)
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print("Connected by {}".format(addr))
            while True:
                data = conn.recv(2048)
                if data:
                    receiver.receive_message(data)
                while True:
                    try:
                        mtu = int(gauss(20, 2))
                        message = receiver.generate_message(mtu)
                        print("Current mtu: {}".format(mtu))
                        s.sendall(b"".join(message.as_bytes()))
                    except RuntimeError as e:
                        break
