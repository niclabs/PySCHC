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
    from schc_messages import All1SCHCFragment
    all1 = All1SCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                            dtag=8, w=2, rcs='0xacde3214')
    all1.add_tile(Tile(b'Hello'))
    all1.add_padding()
    print(all1.as_text())
    from schc_messages import SCHCAck
    ack = SCHCAck(20, protocol=SCHCProtocol.LoRaWAN,
                  dtag=17, w=1, c=False, bitmap=[True] * 63)
    ack.add_padding()
    print(ack.as_bits())
    return regular.as_bytes()[0] + regular.as_bytes()[1]


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(data_to_send())
        data = s.recv(1024)
    print("Received: {}".format(data))
