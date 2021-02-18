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
    from schc_protocols import SCHCProtocol
    from schc_base import Tile
    regular = RegularSCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                                  dtag=4, w=3, fcn=17)
    regular.add_tile(Tile(b'HelloWorld'))
    regular.add_padding()
    print("Send: {}".format(regular.as_bytes()[0] + regular.as_bytes()[1]))
    print(regular.as_text())
    from schc_messages import All1SCHCFragment
    all1 = All1SCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                            dtag=8, w=2, rcs='0xacde3214')
    all1.add_tile(Tile(b'HelloWorld'))
    all1.add_padding()
    print("-----------------------------------------------------------------------------------------------------------")
    print("Send: {}".format(all1.as_bytes()[0] + all1.as_bytes()[1]))
    print(all1.as_text())
    all1 = All1SCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                            dtag=8, w=2, rcs='0xacde3214')
    print("-----------------------------------------------------------------------------------------------------------")
    print("Send: {}".format(all1.as_bytes()[0] + all1.as_bytes()[1]))
    print(all1.as_text())
    from schc_messages import SCHCAck
    ack = SCHCAck(20, protocol=SCHCProtocol.LoRaWAN,
                  dtag=17, w=1, c=False, bitmap=[True] + [False] + ([True] * 61))
    ack.add_padding()
    print("-----------------------------------------------------------------------------------------------------------")
    print("Send: {}".format(ack.as_bytes()[0] + ack.as_bytes()[1]))
    print(ack.as_text())
    from schc_messages import SCHCAckReq
    ack_req = SCHCAckReq(20, protocol=SCHCProtocol.LoRaWAN,
                         dtag=17, w=1)
    ack_req.add_padding()
    print("-----------------------------------------------------------------------------------------------------------")
    print("Send: {}".format(ack_req.as_bytes()[0] + ack_req.as_bytes()[1]))
    print(ack_req.as_text())
    # from schc_messages import SCHCSenderAbort
    # sender_abort = SCHCSenderAbort(20, protocol=SCHCProtocol.LoRaWAN,
    #                                dtag=17, w=1)
    # sender_abort.add_padding()
    # print("-----------------------------------------------------------------------------------------------------------")
    # print("Send: {}".format(sender_abort.as_bytes()[0] + sender_abort.as_bytes()[1]))
    # print(sender_abort.as_text())
    from schc_messages import SCHCReceiverAbort
    receiver_abort = SCHCReceiverAbort(20, protocol=SCHCProtocol.LoRaWAN,
                                       dtag=17, w=1)
    receiver_abort.add_padding()
    print("-----------------------------------------------------------------------------------------------------------")
    print("Send: {}".format(receiver_abort.as_bytes()[0] + receiver_abort.as_bytes()[1]))
    print(receiver_abort.as_text())
    return regular.as_bytes()[0] + regular.as_bytes()[1]


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.send(data_to_send())
        data = s.recv(1024)
    print("Received: {}".format(data))
