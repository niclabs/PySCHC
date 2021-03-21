"""test_dtag: DTag Unit Test"""

from unittest import TestCase, main
from schc_messages.schc_header import DTag


class TestDTag(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        self.dtag = DTag(1, 2)
        self.giant_dtag = DTag(20, 8)
        self.empty_dtag = DTag(1502, 0)

    def test_size(self) -> None:
        self.assertEqual(2, self.dtag.size, "Wrong Size of DTag")
        self.assertEqual(2, self.dtag.t, "T Size of DTag")
        self.assertEqual(8, self.giant_dtag.size, "Wrong Size of Giant DTag")
        self.assertEqual(8, self.giant_dtag.t, "T Size of Giant Bitmap")
        self.assertEqual(0, self.empty_dtag.size, "Wrong Size of Empty DTag")
        self.assertEqual(0, self.empty_dtag.t, "T Size of Empty DTag")

    def test_as_bits(self) -> None:
        self.assertEqual("01", self.dtag.as_bits(), "DTag bits wrong mapped")
        self.assertEqual("00010100", self.giant_dtag.as_bits(), "Giant DTag bits wrong mapped")
        self.assertEqual("", self.empty_dtag.as_bits(), "Empty DTag bits wrong mapped")

    def test_format_text(self) -> None:
        self.assertEqual(
            (" T=2  ", " DTag ", "01    "),
            self.dtag.format_text(),
            "Wrong text generated for DTag"
        )
        self.assertEqual(
            (" T=8    ", " DTag   ", "00010100"),
            self.giant_dtag.format_text(),
            "Wrong text generated for Giant DTag"
        )
        self.assertEqual(
            ("", "", ""),
            self.empty_dtag.format_text(),
            "Wrong text generated for Empty DTag"
        )
        more_giant_dtag = DTag(456, 20)
        self.assertEqual(
            (" T=20               ", " DTag               ", "00000000000111001000"),
            more_giant_dtag.format_text(),
            "Wrong text generated for Really Giant DTag"
        )


if __name__ == '__main__':
    main()
