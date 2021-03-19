""" common_methods on example """

import socket
import logging
from schc_machines import SCHCFiniteStateMachine

HOST = "127.0.0.1"
MTU = 50


def get_mtu() -> int:
    """
    Get MTU size

    Returns
    -------
    int :
        MTU available
    """
    return MTU


def send_socket(msg: bytes, port: int) -> None:
    """
    Send using socket

    Parameters
    ----------
    msg : bytes
        Message to send
    port : int
        Port to use

    Returns
    -------
    None, send message
    """
    sock_tx = socket.socket()
    sock_tx.connect((HOST, port))
    sock_tx.send(msg)
    sock_tx.close()
    return


def receive_socket(socket_rx: socket.socket) -> bytes:
    """
    Receive from socket

    Parameters
    ----------
    socket_rx : socket
        Receiver socket

    Returns
    -------
    bytes :
        Message received
    """
    conn, addr = socket_rx.accept()
    data = conn.recv(1024)
    return data


def messaging_loop(machine: SCHCFiniteStateMachine, socket_rx: socket.socket, sender_port: int) -> None:
    """
    Loop of messages

    Parameters
    ----------
    machine : SCHCFiniteStateMachine
        Machine to execute on loop
    socket_rx : socket
        Socket of receiver
    sender_port : int
        Port to use to sent messages

    Returns
    -------
    None
    """
    exit_all = False
    while True:
        while True:
            try:
                mtu = get_mtu()
                message = machine.generate_message(mtu)
                logging.info("Current mtu: {}".format(mtu))
                send_socket(message.as_bytes(), sender_port)
            except GeneratorExit:
                break
            except SystemExit as e:
                print(e)
                exit_all = True
                break
        if exit_all:
            break
        data = receive_socket(socket_rx)
        if data:
            try:
                machine.receive_message(data)
            except SystemExit as e:
                print(e)
                break
