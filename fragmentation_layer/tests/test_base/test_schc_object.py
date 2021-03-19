""" test_schc_object: Unit testing of SCHCObject static methods """

from unittest import TestCase, main
from schc_base import SCHCObject


class SCHCObjectTest(TestCase):

    def test_bits_2_bytes(self):
        actual = SCHCObject.bits_2_bytes("01001000")
        expected = b'H'
        self.assertEqual(expected, actual, "H wrong decoded")
        hello = "01001000" + "01100101" + "01101100" + "01101100" + "01101111"
        actual = SCHCObject.bits_2_bytes(hello)
        expected = b'Hello'
        self.assertEqual(expected, actual, "H wrong decoded")
        actual = SCHCObject.bits_2_bytes("1001000")
        expected = b'H'
        self.assertEqual(expected, actual, "H wrong decoded")
        actual = SCHCObject.bits_2_bytes("1001")
        expected = b'\t'
        self.assertEqual(expected, actual, "\\t character wrong decoded")
        actual = SCHCObject.bits_2_bytes("1001")
        expected = SCHCObject.bits_2_bytes("00001001")
        self.assertEqual(expected, actual, "\\t character wrong decoded")

    def test_bytes_2_bits(self):
        actual = SCHCObject.bytes_2_bits(b'Hello')
        expected = "01001000" + "01100101" + "01101100" + "01101100" + "01101111"
        self.assertEqual(expected, actual, "Hello wrong encoded")
        actual = SCHCObject.bytes_2_bits(b'a')
        expected = "01100001"
        self.assertEqual(expected, actual, "Letter a wrong encoded")
        actual = SCHCObject.bytes_2_bits(b'1')
        expected = "00110001"
        self.assertEqual(expected, actual, "Number 1 wrong encoded")


if __name__ == '__main__':
    main()
