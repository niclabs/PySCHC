""" test_receiver: Test script Receiver side"""

import socket
import logging

HOST = "127.0.0.1"
PORT = 50007


if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(
        os.pardir,
        "code"
    ))

    logging.basicConfig(level=logging.DEBUG)

    from schc_modes.ack_on_error import AckOnErrorSCHCReceiver
    from schc_protocols import LoRaWAN

    # receiver = AckOnErrorSCHCReceiver(
    #     LoRaWAN(LoRaWAN.UPLINK),
    #     LoRaWAN.UPLINK
    # )

    from schc_parsers import SCHCParser

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print("Connected by {}".format(addr))
            while True:
                data = conn.recv(2048)
                print("Received:")
                print(SCHCParser.from_bytes(LoRaWAN(), data).as_text())
                conn.sendall(b"Ok")
