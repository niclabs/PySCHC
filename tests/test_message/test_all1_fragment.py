""" test_all1_fragment: All1SCHCFragment Unit test """

from unittest import TestCase, main
from schc_messages import All1SCHCFragment
from schc_base import SCHCProtocol, Tile


class TestAll1Fragment(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        self.all1 = All1SCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                                     dtag=4, w=2, rcs='0xacde3214')

    def test_base(self) -> None:
        self.assertEqual(48, self.all1.size, "Wrong size on initialization")
        self.assertEqual(0, self.all1.payload.size, "Payload present before added")
        self.assertEqual(0, self.all1.padding.size, "Padding present before added")
        self.assertEqual(48, self.all1.header.size, "Header size incorrect")
        self.assertEqual(8, self.all1.header.rule_id.size, "Wrong RuleID size")
        self.assertEqual(0, self.all1.header.dtag.size, "Wrong DTag size")
        self.assertEqual(2, self.all1.header.w.size, "Wrong W size")
        self.assertEqual(6, self.all1.header.fcn.size, "Wrong FCN size")
        self.assertEqual(32, self.all1.header.rcs.size, "Wrong RCS size")
        self.assertEqual(0, self.all1.header.c.size, "Wrong IC size")
        self.assertEqual(0, self.all1.header.compressed_bitmap.size, "Wrong Bitmap size")

    def test_add_tile(self) -> None:
        self.assertEqual(0, self.all1.payload.size, "Payload prior initialization")
        init_size = self.all1.size
        first_tile = Tile(b'Hello')
        second_tile = Tile(b' ')
        third_tile = Tile(b'World!')
        payload_size = self.all1.add_tile(first_tile)
        self.assertEqual(payload_size - init_size, first_tile.size, "First tile size got wrong (on return)")
        self.assertEqual(payload_size - init_size, self.all1.payload.size, "First tile size got wrong (on instance)")
        self.assertEqual(payload_size, self.all1.size, "Size got wrong (first)")
        payload_size = self.all1.add_tile(second_tile)
        self.assertEqual(payload_size - init_size, first_tile.size + second_tile.size,
                         "Second tile size got wrong (on return)")
        self.assertEqual(payload_size - init_size, self.all1.payload.size, "Second tile size got wrong (on instance)")
        self.assertEqual(payload_size, self.all1.size, "Size got wrong (second)")
        payload_size = self.all1.add_tile(third_tile)
        self.assertEqual(payload_size - init_size, first_tile.size + second_tile.size + third_tile.size,
                         "Third tile size got wrong (on return)")
        self.assertEqual(payload_size - init_size, self.all1.payload.size, "Third tile size got wrong (on instance)")
        self.assertEqual(payload_size, self.all1.size, "Size got wrong (third)")

    def test_add_padding(self) -> None:
        self.assertEqual(0, self.all1.padding.size, "Pad added (on init)")
        size = self.all1.add_padding()
        self.assertEqual(48, size, "Pad added (on return)")
        self.assertEqual(48, self.all1.size, "Pad added (on instance)")
        self.assertEqual(0, self.all1.padding.size, "Pad added (on padding)")
        payload_size = self.all1.add_tile(Tile(b'Hello'))
        self.assertEqual(48, size, "Pad added (on return)")
        self.assertEqual(payload_size, self.all1.size, "Pad added (on instance)")
        self.assertEqual(0, self.all1.padding.size, "Pad added (on padding)")

    def test_as_bits(self) -> None:
        self.assertEqual(
            "000101001011111110101100110111100011001000010100",
            self.all1.as_bits(),
            "Just header got wrong"
        )
        self.all1.add_tile(Tile(b'Hello'))
        self.all1.add_padding()
        self.assertEqual(
            "0001010010111111101011001101111000110010000101000100100001100101011011000110110001101111",
            self.all1.as_bits(),
            "Message got wrong"
        )

    def test_as_bytes(self) -> None:
        self.assertEqual(
            (b'\x14', b'\xbf\xac\xde2\x14'),
            self.all1.as_bytes(),
            "Just header got wrong"
        )
        self.all1.add_tile(Tile(b'Hello'))
        self.all1.add_padding()
        self.assertEqual(
            (b'\x14', b'\xbf\xac\xde2\x14Hello'),
            self.all1.as_bytes(),
            "Message got wrong"
        )

    def test_as_text(self) -> None:
        self.assertEqual(
            "|--- SCHC Fragment Header                                    ---|\n" +
            "         |-- M=2 --|--- N=6 ---| U=32                           |\n" +
            "| RuleID | W       | FCN       | RCS                            |\n" +
            "|00010100|10       |111111     |10101100110111100011001000010100|",
            self.all1.as_text(),
            "Just header got wrong"
        )
        self.all1.add_tile(Tile(b'Hello'))
        self.all1.add_padding()
        self.assertEqual(
            "|--- SCHC Fragment Header                                    ---|\n" +
            "         |-- M=2 --|--- N=6 ---| U=32                           |\n" +
            "| RuleID | W       | FCN       | RCS                            |" +
            " Fragment Payload                       |\n" +
            "|00010100|10       |111111     |10101100110111100011001000010100|" +
            "0100100001100101011011000110110001101111|",
            self.all1.as_text(),
            "Message got wrong"
        )

    def test_from_bytes(self) -> None:
        all1 = All1SCHCFragment.from_bytes(b'\x14\xd1Hello')
        """
        self.assertEqual(
            "|--- SCHC Fragment Header                                    ---|\n" +
            "         |-- M=2 --|--- N=6 ---| U=32                           |\n" +
            "| RuleID | W       | FCN       | RCS                            |" +
            " Fragment Payload                       |\n" +
            "|00010100|10       |111111     |10101100110111100011001000010100|" + 
            "0100100001100101011011000110110001101111|",
            self.all1.as_text(),
            "Message parsed wrong"
        )
        """


if __name__ == '__main__':
    main()
