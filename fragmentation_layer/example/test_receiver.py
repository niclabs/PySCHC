""" test_receiver: Test script Receiver side"""

import logging
import socket
import json
import requests

from common_methods import HOST, MTU, send_socket, receive_socket, is_this_loss, get_mtu

RECEIVER_PORT = 50006
SENDER_PORT = 50007

socket_rx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_rx.settimeout(10)
socket_rx.bind((HOST, RECEIVER_PORT))
socket_rx.listen(1)


if __name__ == '__main__':
    """
    This should work as a server
    """
    logging.basicConfig(level=logging.DEBUG)

    while True:
        try:
            data = receive_socket(socket_rx)
            if data:
                requests.post(
                    "http://{}:{}/test".format(HOST, 5000),
                    json={
                        "port": int(data[0]),
                        "dev_id": "",
                        "downlink_url": "http://{}:{}/to_socket".format(
                            HOST, 5000
                        ),
                        "payload_raw": data[1:].decode("utf-8")
                    })
        except socket.timeout:
            pass

    # packet = handler.payload.as_bits()
    # assert len(packet) % 8 == 0
    #
    # from schc_base import SCHCObject
    # message = SCHCObject.bits_2_bytes(packet)
    # with open("received.txt", "w", encoding="utf-8") as received_file:
    #     received_file.write(message.decode("ascii"))
