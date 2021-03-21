""" test_regular_fragment: RegularSCHCFragment Unit test """

from unittest import TestCase, main
from schc_messages import RegularSCHCFragment
from schc_base import Tile
from schc_protocols import SCHCProtocol


class TestRegularFragment(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        self.regular = RegularSCHCFragment(20, protocol=SCHCProtocol.LoRaWAN,
                                           dtag=4, w=3, fcn=17)

    def test_base(self) -> None:
        self.assertEqual(16, self.regular.size, "Wrong size on initialization")
        self.assertEqual(0, self.regular.payload.size, "Payload present before added")
        self.assertEqual(0, self.regular.padding.size, "Padding present before added")
        self.assertEqual(16, self.regular.header.size, "Header size incorrect")
        self.assertEqual(8, self.regular.header.rule_id.size, "Wrong RuleID size")
        self.assertEqual(0, self.regular.header.dtag.size, "Wrong DTag size")
        self.assertEqual(2, self.regular.header.w.size, "Wrong W size")
        self.assertEqual(6, self.regular.header.fcn.size, "Wrong FCN size")
        self.assertEqual(0, self.regular.header.rcs.size, "Wrong RCS size")
        self.assertEqual(0, self.regular.header.c.size, "Wrong IC size")
        self.assertEqual(0, self.regular.header.compressed_bitmap.size, "Wrong Bitmap size")

    def test_add_tile(self) -> None:
        self.assertEqual(0, self.regular.payload.size, "Payload prior initialization")
        init_size = self.regular.size
        first_tile = Tile(b'Hello')
        second_tile = Tile(b' ')
        third_tile = Tile(b'World!')
        payload_size = self.regular.add_tile(first_tile)
        self.assertEqual(payload_size - init_size, first_tile.size, "First tile size got wrong (on return)")
        self.assertEqual(payload_size - init_size, self.regular.payload.size, "First tile size got wrong (on instance)")
        self.assertEqual(payload_size, self.regular.size, "Size got wrong (first)")
        payload_size = self.regular.add_tile(second_tile)
        self.assertEqual(payload_size - init_size, first_tile.size + second_tile.size, "Second tile size got wrong (on return)")
        self.assertEqual(payload_size - init_size, self.regular.payload.size, "Second tile size got wrong (on instance)")
        self.assertEqual(payload_size, self.regular.size, "Size got wrong (second)")
        payload_size = self.regular.add_tile(third_tile)
        self.assertEqual(payload_size - init_size, first_tile.size + second_tile.size + third_tile.size,
                         "Third tile size got wrong (on return)")
        self.assertEqual(payload_size - init_size, self.regular.payload.size, "Third tile size got wrong (on instance)")
        self.assertEqual(payload_size, self.regular.size, "Size got wrong (third)")

    def test_add_padding(self) -> None:
        self.assertEqual(0, self.regular.padding.size, "Pad added (on init)")
        size = self.regular.add_padding()
        self.assertEqual(16, size, "Pad added (on return)")
        self.assertEqual(16, self.regular.size, "Pad added (on instance)")
        self.assertEqual(0, self.regular.padding.size, "Pad added (on padding)")
        payload_size = self.regular.add_tile(Tile(b'Hello'))
        self.assertEqual(16, size, "Pad added (on return)")
        self.assertEqual(payload_size, self.regular.size, "Pad added (on instance)")
        self.assertEqual(0, self.regular.padding.size, "Pad added (on padding)")

    def test_as_bits(self) -> None:
        self.assertEqual(
            "0001010011010001",
            self.regular.as_bits(),
            "Just header got wrong"
        )
        self.regular.add_tile(Tile(b'Hello'))
        self.regular.add_padding()
        self.assertEqual(
            "00010100110100010100100001100101011011000110110001101111",
            self.regular.as_bits(),
            "Message got wrong"
        )

    def test_as_bytes(self) -> None:
        self.assertEqual(
            (b'\x14', b'\xd1'),
            self.regular.as_bytes(),
            "Just header got wrong"
        )
        self.regular.add_tile(Tile(b'Hello'))
        self.regular.add_padding()
        self.assertEqual(
            (b'\x14', b'\xd1Hello'),
            self.regular.as_bytes(),
            "Message got wrong"
        )

    def test_as_text(self) -> None:
        self.assertEqual(
            "|--- SCHC Fragment Header   ---|\n" +
            "         |-- M=2 --|--- N=6 ---|\n" +
            "| RuleID | W       | FCN       |\n" +
            "|00010100|11       |010001     |",
            self.regular.as_text(),
            "Just header got wrong"
        )
        self.regular.add_tile(Tile(b'Hello'))
        self.regular.add_padding()
        self.assertEqual(
            "|--- SCHC Fragment Header   ---|\n" +
            "         |-- M=2 --|--- N=6 ---|\n" +
            "| RuleID | W       | FCN       | Fragment Payload                       |\n" +
            "|00010100|11       |010001     |0100100001100101011011000110110001101111|",
            self.regular.as_text(),
            "Message got wrong"
        )

    def test_from_bytes(self) -> None:
        regular = RegularSCHCFragment.from_bytes(b'\x14\xd1HelloWorld')
        self.assertEqual(
            "|--- SCHC Fragment Header   ---|\n" +
            "         |-- M=2 --|--- N=6 ---|\n" +
            "| RuleID | W       | FCN       |" +
            " Fragment Payload                                                               |\n" +
            "|00010100|11       |010001     |" +
            "01001000011001010110110001101100011011110101011101101111011100100110110001100100|",
            regular.as_text(),
            "Message parsed wrong"
        )


if __name__ == '__main__':
    main()
