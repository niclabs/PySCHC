""" test_sender: Test script Sender side"""

import logging
import socket
from common_methods import messaging_loop, HOST, get_mtu, send_socket, receive_socket

RECEIVER_PORT = 50007
SENDER_PORT = 50006

MESSAGE = """
Abstract

   The Static Context Header Compression (SCHC) specification describes
   generic header compression and fragmentation techniques for Low Power
   Wide Area Networks (LPWAN) technologies.  SCHC is a generic mechanism
   designed for great flexibility so that it can be adapted for any of
   the LPWAN technologies.

   This document specifies a profile of RFC8724 to use SCHC in
   LoRaWAN(R) networks, and provides elements such as efficient
   parameterization and modes of operation.

Status of This Memo

   This Internet-Draft is submitted in full conformance with the
   provisions of BCP 78 and BCP 79.

   Internet-Drafts are working documents of the Internet Engineering
   Task Force (IETF).  Note that other groups may also distribute
   working documents as Internet-Drafts.  The list of current Internet-
   Drafts is at https://datatracker.ietf.org/drafts/current/.

   Internet-Drafts are draft documents valid for a maximum of six months
   and may be updated, replaced, or obsoleted by other documents at any
   time.  It is inappropriate to use Internet-Drafts as reference
   material or to cite them other than as "work in progress."

   This Internet-Draft will expire on July 29, 2021.

Copyright Notice

   Copyright (c) 2021 IETF Trust and the persons identified as the
   document authors.  All rights reserved.

   This document is subject to BCP 78 and the IETF Trust's Legal
   Provisions Relating to IETF Documents
   (https://trustee.ietf.org/license-info) in effect on the date of
   publication of this document.  Please review these documents 
   carefully, as they describe your rights and restrictions with respect
   to this document.  Code Components extracted from this document must
   include Simplified BSD License text as described in Section 4.e of
   the Trust Legal Provisions and are provided without warranty as
   described in the Simplified BSD License.
""".encode("ascii")

RESIDUE = "0101100"

socket_rx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_rx.bind((HOST, RECEIVER_PORT))
socket_rx.listen(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    from schc_machines.lorawan import UplinkSender
    from schc_protocols import LoRaWAN

    sender = UplinkSender(
        LoRaWAN(LoRaWAN.UPLINK),
        MESSAGE,
        RESIDUE
    )

    messaging_loop(sender, socket_rx, SENDER_PORT)
