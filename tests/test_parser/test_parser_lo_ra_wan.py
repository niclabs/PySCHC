""" test_parser_lo_ra_wan: Unit test for parsing over LoRaWAN """

from unittest import TestCase, main
from schc_parsers import SCHCParser
from schc_protocols import LoRaWAN


class TestParserLoRaWAN(TestCase):

    def test_regular(self):
        # Uplink
        expected_regular = SCHCParser.from_bytes(LoRaWAN(), b'\x14\xd1HelloWorld')
        self.assertEqual(
            "|--- SCHC Fragment Header   ---|\n" +
            "         |-- M=2 --|--- N=6 ---|\n" +
            "| RuleID | W       | FCN       |" +
            " Fragment Payload                                                               |\n" +
            "|00010100|11       |010001     |" +
            "01001000011001010110110001101100011011110101011101101111011100100110110001100100|",
            expected_regular.as_text(),
            "SCHCRegular not parsed (uplink mode)"
        )
        # Downlink
        # TODO
        expected_regular = None
        self.assertEqual(
            None,
            expected_regular,  # .as_text(),
            "SCHCRegular not parsed (downlink mode)"
        )

    def test_all1(self):
        # Uplink
        # With Payload
        expected_all1 = SCHCParser.from_bytes(LoRaWAN(), b'\x14\xbf\xac\xde2\x14HelloWorld')
        self.assertEqual(
            "|--- SCHC Fragment Header                                    ---|\n" +
            "         |-- M=2 --|--- N=6 ---| U=32                           |\n" +
            "| RuleID | W       | FCN       | RCS                            |" +
            " Fragment Payload                                                               |\n" +
            "|00010100|10       |111111     |10101100110111100011001000010100|" +
            "01001000011001010110110001101100011011110101011101101111011100100110110001100100|",
            expected_all1.as_text(),
            "SCHCAll1 not parsed (uplink mode, with payload)"
        )
        # Uplink
        # Without Payload
        expected_all1 = SCHCParser.from_bytes(LoRaWAN(), b'\x14\xbf\xac\xde2\x14')
        self.assertEqual(
            "|--- SCHC Fragment Header                                    ---|\n" +
            "         |-- M=2 --|--- N=6 ---| U=32                           |\n" +
            "| RuleID | W       | FCN       | RCS                            |\n" +
            "|00010100|10       |111111     |10101100110111100011001000010100|",
            expected_all1.as_text(),
            "SCHCAll1 not parsed (uplink mode, without payload)"
        )
        # Downlink
        # TODO
        expected_all1 = None
        self.assertEqual(
            None,
            expected_all1,  # .as_text(),
            "SCHCAll1 not parsed (downlink mode)"
        )

    def test_ack(self):
        # Uplink
        expected_ack = SCHCParser.from_bytes(LoRaWAN(), b'\x14W')
        self.assertEqual(
            "|-- SCHC ACK Header  --|\n" +
            "         |-- M=2 --| 1 |\n" +
            "| RuleID | W       | C | Compressed Bitmap |\n" +
            "|00010100|01       | 0 |10111              |",
            expected_ack.as_text(),
            "SCHC Ack not parsed (uplink mode)"
        )
        # Downlink
        # TODO
        expected_ack = None
        self.assertEqual(
            None,
            expected_ack,  # .as_text(),
            "SCHC Ack not parsed (downlink mode)"
        )

    def test_acq_req(self):
        # Uplink
        expected_ack_req = SCHCParser.from_bytes(LoRaWAN(), b'\x14@')
        self.assertEqual(
            "|- SCHC ACK REQ Header        -|\n" +
            "         |-- M=2 --|--- N=6 ---|\n" +
            "| RuleID | W       | FCN       |\n" +
            "|00010100|01       |000000     |",
            expected_ack_req.as_text(),
            "SCHC ACK Request not parsed (uplink mode)"
        )
        # Downlink
        # TODO
        expected_ack_req = None
        self.assertEqual(
            None,
            expected_ack_req,  # .as_text(),
            "SCHC ACK Request not parsed (downlink mode)"
        )

    def test_receiver_abort(self):
        # Uplink
        expected_rec_abort = SCHCParser.from_bytes(LoRaWAN(), b'\x14\xff\xff')
        self.assertEqual(
            "| Receiver-Abort Header|\n" +
            "         |-- M=2 --| 1 |\n" +
            "| RuleID | W       | C |\n" +
            "|00010100|11       | 1 |11111|11111111|",
            expected_rec_abort.as_text(),
            "SCHC Receiver Abort not parsed (uplink mode)"
        )
        # Downlink
        # TODO
        expected_rec_abort = None
        self.assertEqual(
            None,
            expected_rec_abort,  # .as_text(),
            "SCHC Receiver Abort not parsed (downlink mode)"
        )


if __name__ == '__main__':
    main()
