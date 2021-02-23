"""test_bitmap: Compressed Bitmap Unit Test"""

from unittest import TestCase, main
from schc_messages.schc_header import CompressedBitmap


class TestCompressedBitmap(TestCase):

    def setUp(self) -> None:
        """
        Sets up unit test

        Returns
        -------
        None
        """
        self.bitmap = CompressedBitmap([True, False, False, True], 4)
        self.un_bitmap = CompressedBitmap([True, False], 5)
        self.empty_bitmap = CompressedBitmap([], 0)

    def test_wrong_bitmap_size(self) -> None:
        self.assertRaises(AssertionError, CompressedBitmap, [True] * 10, 8)

    def test_fill_up(self) -> None:
        self.assertEqual(2, len(self.un_bitmap.bitmap), "Filled up length wrong")
        self.assertEqual(
            [True, False],
            self.un_bitmap.bitmap,
            "Filled up values wrong"
        )

    def test_size(self) -> None:
        self.assertEqual(4, self.bitmap.size, "Wrong Size of Bitmap")
        self.assertEqual(4, self.bitmap.window_size, "Wrong Window Size of Bitmap")
        self.assertEqual(2, self.un_bitmap.size, "Wrong Size of Filled up Bitmap")
        self.assertEqual(5, self.un_bitmap.window_size, "Wrong Window Size of Filled up Bitmap")
        self.assertEqual(0, self.empty_bitmap.size, "Wrong Size of Empty Bitmap")
        self.assertEqual(0, self.empty_bitmap.window_size, "Wrong Window Size of Empty Bitmap")

    def test_as_bits(self) -> None:
        self.assertEqual("1001", self.bitmap.as_bits(), "Bitmap bits wrong mapped")
        self.assertEqual("10", self.un_bitmap.as_bits(), "Filled Up Bitmap bits wrong mapped")
        self.assertEqual("", self.empty_bitmap.as_bits(), "Empty Bitmap bits wrong mapped")

    def test_format_text(self) -> None:
        self.assertEqual(
            ("", " Compressed Bitmap ", "1001               "),
            self.bitmap.format_text(),
            "Wrong text generated for Bitmap"
        )
        self.assertEqual(
            ("", " Compressed Bitmap ", "10                 "),
            self.un_bitmap.format_text(),
            "Wrong text generated for Filled up Bitmap"
        )
        self.assertEqual(
            ("", "", ""),
            self.empty_bitmap.format_text(),
            "Wrong text generated for Empty Bitmap"
        )
        giant_bitmap = CompressedBitmap([True] * 25, 25)
        self.assertEqual(
            ("", " Compressed Bitmap       ", "1"*25),
            giant_bitmap.format_text(),
            "Wrong text generated for Empty Bitmap"
        )


if __name__ == '__main__':
    main()
