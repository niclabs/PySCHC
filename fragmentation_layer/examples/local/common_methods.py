""" common_methods on example """

import random
import socket
from schc_machines import SCHCFiniteStateMachine

HOST = "127.0.0.1"
MTU = 50
SEED = 7
PROBABILITY_OF_FAILURE = 0.2

random.seed(SEED)


def get_mtu() -> int:
    """
    Get MTU size

    Returns
    -------
    int :
        MTU available
    """
    return MTU


def is_this_loss() -> bool:
    """
    Returns whether the send process was done

    Returns
    -------
    bool :
        True if sent does not occur
    """
    return random.random() < PROBABILITY_OF_FAILURE


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
    while True:
        mtu = get_mtu()
        lost = is_this_loss()
        try:
            print("Sending...")
            print("Messages enqueued: {}".format(machine.message_to_send))
            message = machine.generate_message(mtu)
            print("Current mtu: {}".format(mtu))
            print("Package sent: {}".format(not lost))
            if isinstance(machine.state, SCHCFiniteStateMachine.EndState):
                send_socket(message.as_bytes(), sender_port)
            elif not lost and message is not None:
                send_socket(message.as_bytes(), sender_port)
        except SystemExit as e:
            print(e)
            break
        try:
            print("Receiving...")
            data = receive_socket(socket_rx)
            if data:
                try:
                    machine.receive_message(data)
                except SystemExit as e:
                    print(e)
                    break
        except socket.timeout:
            pass
