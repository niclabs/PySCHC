""" test_receiver: Test script Receiver side"""

import socket

HOST = "127.0.0.1"
PORT = 50007


def parse_received(received: bytes) -> bytes:
    """
    Parse data received from socket

    Parameters
    ----------
    received : bytes
        Data received

    Returns
    -------
    bytes :
        Returned message
    """
    from schc_base import SCHCProtocol
    from schc_messages import RegularSCHCFragment
    regular = RegularSCHCFragment.from_bytes(received, protocol=SCHCProtocol.LoRaWAN)
    print(regular.as_text())
    print("Received: {}".format(RegularSCHCFragment.bits_2_bytes(regular.payload.content)))
    return b"Ok"


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print("Connected by {}".format(addr))
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(parse_received(data))
