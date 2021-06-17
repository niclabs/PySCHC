""" test_bitmap: Unit test for Bitmap class """

from unittest import TestCase, main
from schc_base import Bitmap
from schc_protocols import LoRaWAN


class TestBitmap(TestCase):

    def test_constructor(self):
        bitmap = Bitmap(LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR))
        self.assertEqual([False] * LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR).WINDOW_SIZE, bitmap.__bitmap__,
                         "Wrong bitmap generated")
        self.assertEqual(LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR).WINDOW_SIZE, len(bitmap.__bitmap__), "Wrong length of bitmap")
        bitmap = Bitmap(LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR), short_size=10)
        self.assertEqual([False] * 10, bitmap.__bitmap__, "Wrong bitmap generated (short)")
        self.assertEqual(10, len(bitmap.__bitmap__), "Wrong length of bitmap (short)")

    def test_register_tile(self):
        bitmap = Bitmap(LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR))
        bitmap.tile_received(LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR).WINDOW_SIZE - 1)
        self.assertTrue(bitmap.__bitmap__[0], "Wrong first tile registered")
        fcn = 30
        bitmap.tile_received(fcn)
        self.assertTrue(bitmap.__bitmap__[LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR).WINDOW_SIZE - fcn - 1],
                        "Wrong tile registered {}".format(fcn))
        bitmap.tile_received(0)
        self.assertTrue(bitmap.__bitmap__[LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR).WINDOW_SIZE - 1],
                        "Wrong last tile registered")
        self.assertEqual(LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR).WINDOW_SIZE, len(bitmap.__bitmap__),
                         "Length changed")
        self.assertEqual(3, sum(bitmap.__bitmap__), "Wrong registration")

    def test_compression_all_one(self):
        protocol_to_use = LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR)
        bitmap = Bitmap(protocol_to_use)
        bitmap.__bitmap__ = [True] * protocol_to_use.WINDOW_SIZE
        compressed_bitmap = bitmap.generate_compress()
        self.assertEqual(
            protocol_to_use.L2_WORD - (sum([
                protocol_to_use.RULE_SIZE, protocol_to_use.T, protocol_to_use.M, 1
            ]) % protocol_to_use.L2_WORD),
            len(compressed_bitmap), "Wrong compression")
        self.assertEqual(
            protocol_to_use.L2_WORD - (sum([
                protocol_to_use.RULE_SIZE, protocol_to_use.T, protocol_to_use.M, 1
            ]) % protocol_to_use.L2_WORD),
            sum(compressed_bitmap), "Wrong compression")

    def test_compression_uncompressed(self):
        protocol_to_use = LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR)
        bitmap = Bitmap(protocol_to_use)
        compressed_bitmap = bitmap.generate_compress()
        self.assertEqual(protocol_to_use.WINDOW_SIZE, len(compressed_bitmap), "Wrong compression")
        self.assertEqual(0, sum(compressed_bitmap), "Wrong compression")

    def test_compression(self):
        protocol_to_use = LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR)
        bitmap = Bitmap(protocol_to_use)
        bitmap.__bitmap__ = [True] * protocol_to_use.WINDOW_SIZE
        bitmap.__bitmap__[protocol_to_use.L2_WORD] = False
        compressed_bitmap = bitmap.generate_compress()
        self.assertEqual(
            protocol_to_use.L2_WORD - (sum([
                protocol_to_use.RULE_SIZE, protocol_to_use.T,
                protocol_to_use.M, 1
            ]) % protocol_to_use.L2_WORD) + protocol_to_use.L2_WORD,
            len(compressed_bitmap), "Wrong compression")
        self.assertEqual(
            protocol_to_use.L2_WORD - (sum([
                protocol_to_use.RULE_SIZE, protocol_to_use.T, protocol_to_use.M, 1
            ]) % protocol_to_use.L2_WORD) + protocol_to_use.L2_WORD - 1,
            sum(compressed_bitmap), "Wrong compression")

    def test_has_missing(self):
        protocol = LoRaWAN(LoRaWAN.ACK_ON_ERROR)
        bitmap = Bitmap(protocol)
        self.assertFalse(bitmap.has_missing(), "Bitmap full False has missing")
        bitmap.tile_received(protocol.WINDOW_SIZE - 1)
        self.assertFalse(bitmap.has_missing(), "Bitmap first one has missing")
        for i in range(5):
            bitmap.tile_received(protocol.WINDOW_SIZE - (i + 2))
        self.assertFalse(bitmap.has_missing(), "Bitmap first ones has missing")
        for i in range(5):
            bitmap.tile_received(protocol.WINDOW_SIZE - (i + 10))
        self.assertTrue(bitmap.has_missing(), "Bitmap has missing not reported")
        for i in range(5):
            bitmap.tile_received(protocol.WINDOW_SIZE - (i + 20))
        self.assertTrue(bitmap.has_missing(), "Bitmap has missing not reported (second case)")
        for i in range(protocol.WINDOW_SIZE):
            bitmap.tile_received(protocol.WINDOW_SIZE - (i + 1))
        self.assertFalse(bitmap.has_missing(), "Bitmap full True has missing")

    def test_get_missing(self):
        protocol = LoRaWAN(LoRaWAN.ACK_ON_ERROR)
        bitmap = Bitmap(protocol)
        self.assertEqual(0, bitmap.get_missing(), "fcn = False, after = None")
        bitmap.tile_received(protocol.WINDOW_SIZE - 5)  # 63 - 5 = 58, index = 4
        self.assertEqual(0, bitmap.get_missing(), "fcn = False, after = None (with one tile)")
        self.assertEqual(7, bitmap.get_missing(after=6), "fcn = False, after = 6 (with one tile)")
        self.assertEqual(56, bitmap.get_missing(fcn=True, after=57), "fcn = True, after = 57 (with one tile)")
        for i in range(5):
            bitmap.tile_received(protocol.WINDOW_SIZE - (i + 1))
        self.assertEqual(5, bitmap.get_missing(), "fcn = False, after = None (with six tiles)")
        self.assertEqual(57, bitmap.get_missing(fcn=True), "fcn = True, after = None (with six tiles)")
        self.assertEqual(5, bitmap.get_missing(after=4), "fcn = False, after = 4 (with one tile)")
        self.assertEqual(57, bitmap.get_missing(fcn=True, after=62), "fcn = True, after = 55 (with one tile)")


if __name__ == '__main__':
    main()
