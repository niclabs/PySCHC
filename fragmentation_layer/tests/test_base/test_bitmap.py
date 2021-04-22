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


if __name__ == '__main__':
    main()
