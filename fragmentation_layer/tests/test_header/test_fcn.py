"""test_fcn: Fragment Compressed Number Unit Test"""

from unittest import TestCase, main
from schc_messages.schc_header import FragmentedCompressedNumber


class TestFragmentCompressedNumber(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        self.fcn = FragmentedCompressedNumber(56, 6)
        self.giant_fcn = FragmentedCompressedNumber(185, 10)
        self.mini_fcn = FragmentedCompressedNumber(0, 2)
        self.empty_fcn = FragmentedCompressedNumber(0, 0)

    def test_wrong_fcn_size(self) -> None:
        self.assertRaises(AssertionError, FragmentedCompressedNumber, 64, 6)

    def test_size(self) -> None:
        self.assertEqual(6, self.fcn.size, "Wrong Size of FCN")
        self.assertEqual(6, self.fcn.n, "N Size of FCN")
        self.assertEqual(10, self.giant_fcn.size, "Wrong Size of Giant FCN")
        self.assertEqual(10, self.giant_fcn.n, "N Size of Giant FCN")
        self.assertEqual(2, self.mini_fcn.size, "Wrong Size of Mini FCN")
        self.assertEqual(2, self.mini_fcn.n, "N Size of Mini FCN")
        self.assertEqual(0, self.empty_fcn.size, "Wrong Size of Empty FCN")
        self.assertEqual(0, self.empty_fcn.n, "N Size of Empty FCN")

    def test_as_bits(self) -> None:
        self.assertEqual("111000", self.fcn.as_bits(), "FCN bits wrong mapped")
        self.assertEqual("0010111001", self.giant_fcn.as_bits(), "Giant FCN bits wrong mapped")
        self.assertEqual("00", self.mini_fcn.as_bits(), "Mini FCN bits wrong mapped")
        self.assertEqual("", self.empty_fcn.as_bits(), "Empty FCN bits wrong mapped")

    def test_format_text(self) -> None:
        self.assertEqual(
            ("--- N=6 ---", " FCN       ", "111000     "),
            self.fcn.format_text(),
            "Wrong text generated for FCN"
        )
        self.assertEqual(
            ("--- N=10 ---", " FCN        ", "0010111001  "),
            self.giant_fcn.format_text(),
            "Wrong text generated for Giant FCN"
        )
        self.assertEqual(
            ("--- N=2 ---", " FCN       ", "00         "),
            self.mini_fcn.format_text(),
            "Wrong text generated for Mini FCN"
        )
        self.assertEqual(
            ("", "", ""),
            self.empty_fcn.format_text(),
            "Wrong text generated for Empty FCN"
        )
        more_giant_fcn = FragmentedCompressedNumber(185, 13)
        self.assertEqual(
            ("--- N=13  ---", " FCN         ", "0000010111001"),
            more_giant_fcn.format_text(),
            "Wrong text generated for Really Giant FCN"
        )


if __name__ == '__main__':
    main()
