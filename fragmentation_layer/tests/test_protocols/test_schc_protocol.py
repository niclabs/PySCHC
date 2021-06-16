""" test_schc_protocol: SCHC Protocol unit test class """

from binascii import crc32
from random import seed, choices, choice
from unittest import TestCase, main
from schc_base import SCHCObject
from schc_protocols import LoRaWAN

SEED = 7
SHORT_MESSAGE = "This is a short message".encode("ascii")
LONG_MESSAGE = """
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
WORD_LENGTHS = [10, 200, int(1e3)]


class TestSCHCProtocol(TestCase):

    def test_crc32_static_message(self) -> None:
        short = SCHCObject.bytes_2_bits(SHORT_MESSAGE)
        library = hex(crc32(SCHCObject.bits_2_bytes(short)))
        local = LoRaWAN().calculate_rcs(short)
        self.assertEqual(library, local, "Short message crc32 do not match")
        long = SCHCObject.bytes_2_bits(LONG_MESSAGE)
        library = hex(crc32(SCHCObject.bits_2_bytes(long)))
        local = LoRaWAN().calculate_rcs(long)
        self.assertEqual(library, local, "Long message crc32 do not match")

    def test_crc32_random(self) -> None:
        seed(SEED)
        import string
        for _ in range(100):
            a_word = "".join(
                choices(string.ascii_letters, k=choice(WORD_LENGTHS))
            ).encode("ascii")
            word = SCHCObject.bytes_2_bits(a_word)
            library = hex(crc32(SCHCObject.bits_2_bytes(word)))
            local = LoRaWAN().calculate_rcs(word)
            self.assertEqual(
                library, local,
                "Random message {} crc32 do not match".format(a_word)
            )


if __name__ == '__main__':
    main()
