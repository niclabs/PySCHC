""" test_sender: Test script Sender side"""

import logging
import socket

from message import MESSAGE
from common_methods import HOST, MTU, get_mtu, is_this_loss, send_socket, receive_socket

RECEIVER_PORT = 50007
SENDER_PORT = 50006

RESIDUE = "0101100"

socket_rx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_rx.settimeout(1)
socket_rx.bind((HOST, RECEIVER_PORT))
socket_rx.listen(1)


class TestSocket:

    def __init__(self, a_socket, port):
        self.__socket__ = a_socket
        self.__port__ = port
        self.__f_port__ = 0
        return

    def bind(self, f_port):
        """
        Bind method equivalent to pycom.socket.bind

        Parameters
        ----------
        f_port : int
            FPort of SCHC Message

        Returns
        -------
        None
        """
        self.__f_port__ = f_port
        return

    def setblocking(self, block):
        """
        Block the socket

        Parameters
        ----------
        block : bool
            Whether or not keep the socket blocked

        Returns
        -------
        None
        """
        self.__socket__.setblocking(block)
        return

    def send(self, content):
        """
        Send a message

        Parameters
        ----------
        content : bytes
            Bytes to send

        Returns
        -------
        None
        """
        send_socket(bytes([self.__f_port__]) + content, self.__port__)
        return

    def recvfrom(self, buffer_size):
        """
        Receives a message from gateway

        Parameters
        ----------
        buffer_size : int
            Size of the buffer

        Returns
        -------
        Tuple[bytes, int]
            Message received and FPort of message
        """
        try:
            data = receive_socket(self.__socket__)
            return data[1:], int(data[0])
        except BlockingIOError:
            return b'', 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    s = TestSocket(socket_rx, SENDER_PORT)

    from schc_handlers import SCHCNodeHandler
    from schc_protocols import SCHCProtocol

    handler = SCHCNodeHandler(SCHCProtocol.LoRaWAN, MTU)
    handler.send_package(MESSAGE)
    handler.start(s)
