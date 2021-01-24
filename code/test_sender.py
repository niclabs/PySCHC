""" test_sender: Test script Sender side"""

import socket

HOST = "127.0.0.1"
PORT = 50007


def data_to_send() -> bytes:
    """
    Data to send to socket

    Returns
    -------
    bytes :
        Data to send
    """
    from schc_messages import RegularSCHCFragment
    from schc_base import SCHCProtocol, Tile
    regular = RegularSCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                                  dtag=4, w=3, fcn=17)
    regular.add_tile(Tile(b'Hello'))
    regular.add_padding()
    print("Send: {}".format(regular.as_bytes()[0] + regular.as_bytes()[1]))
    print(regular.as_text())
    return regular.as_bytes()[0] + regular.as_bytes()[1]


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(data_to_send())
        data = s.recv(1024)
    print("Received: {}".format(data))
