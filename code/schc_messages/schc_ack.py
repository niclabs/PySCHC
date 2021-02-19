"""schc_ack: SCHCAck Class"""

from typing import List
from schc_messages import SCHCMessage


class SCHCAck(SCHCMessage):
    """
    SCHC Ack Class

    |---- SCHC ACK Header ----|
             |--T---|-M-|- 1 -|Compressed Bitmap|
    +--------+------+---+-----+-----------------+--------------------+
    | RuleID | Dtag | W |  C  |Compressed Bitmap| padding (as needed)|
    +--------+------+---+-----+-----------------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int, c: bool, dtag: int = None,
                 w: int = None, bitmap: List[bool] = None, compress: bool = True) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id
        protocol
        c
        dtag
        w
        bitmap
        compress : bool, optional
            Whether or not to compress bitmap. Default True.
            It is recommended to use compress=False if is the result of a parsing
        """
        assert (w is None or c) or bitmap is not None,\
            "If windows are used and c is True, bitmap must be specified"
        super().__init__(rule_id=rule_id, protocol=protocol, dtag=dtag,
                         w=w, c=c, bitmap=bitmap)
        if compress:
            self.compress_bitmap()

    def as_bits(self) -> str:
        """
        Bits sequence representation

        Returns
        -------
        str :
            Bits sequence in a string
        """
        return self.header.as_bits() + self.padding.as_bits()

    def compress_bitmap(self) -> None:
        """
        Compress Bitmap of ACK Message

        Returns
        -------
        Alter self (bitmap)
        """
        if self.header.compressed_bitmap.size == 1:
            pass
        else:
            temporary_message = self.as_bits()
            no_bitmap_header_length = len(temporary_message) - self.header.compressed_bitmap.window_size
            scissor = len(temporary_message)
            while temporary_message[scissor - 1] == "1" and scissor > no_bitmap_header_length:
                scissor -= 1
            while scissor % self.protocol.L2_WORD != 0 and scissor > no_bitmap_header_length:
                scissor += 1
            compress_bitmap = temporary_message[no_bitmap_header_length:scissor]
            compress_bitmap = [bit == "1" for bit in compress_bitmap]
            self.header.compressed_bitmap.bitmap = compress_bitmap
            self.header.compressed_bitmap.size = len(compress_bitmap)
            self.header.size = scissor
            self.size = scissor
        return

    def as_text(self) -> str:
        """
        Writes ACK message with specifications

        Returns
        -------
        str :
            SCHC ACK Message as text format
        """
        header_text = "|-- SCHC ACK Header {}--|\n"
        return self.base_as_text(header_text)

    @staticmethod
    def from_bytes(received: bytes, protocol: int = 1) -> SCHCMessage:
        """
        Generates a SCHCAck instance from bytes

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received, default LoRaWAN

        Returns
        -------
        SCHCMessage :
            An new instance of SCHC Ack
        """
        protocol_to_use, bits_received, pointer, rule_id, dtag, w = SCHCAck._get_common_(received, protocol=protocol)
        c = bits_received[pointer:pointer + 1] == "1"
        pointer += 1
        if c:
            message = SCHCAck(rule_id, protocol=protocol,
                              c=c, dtag=dtag, w=w)
            message.add_padding()
        else:
            bitmap = bits_received[pointer:]
            if len(bitmap) > protocol_to_use.WINDOW_SIZE:
                bitmap = bitmap[0:protocol_to_use.WINDOW_SIZE]
                bitmap = [i == "1" for i in bitmap]
                message = SCHCAck(rule_id, protocol=protocol, c=c,
                                  dtag=dtag, w=w, bitmap=bitmap)
                message.add_padding()
            else:
                bitmap = [i == "1" for i in bitmap]
                message = SCHCAck(rule_id, protocol=protocol, c=c,
                                  dtag=dtag, w=w, bitmap=bitmap)
        return message
