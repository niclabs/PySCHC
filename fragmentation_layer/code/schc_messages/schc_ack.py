"""schc_ack: SCHCAck Class"""

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

    def __init__(self, rule_id, protocol, c, dtag=None, w=None, compressed_bitmap=None):
        """
        Constructor

        Parameters
        ----------
        rule_id
        protocol
        c
        dtag
        w
        compressed_bitmap
        """
        assert (w is None or c) or compressed_bitmap is not None,\
            "If windows are used and c is True, bitmap must be specified"
        super().__init__(rule_id=rule_id, protocol=protocol, dtag=dtag,
                         w=w, c=c, compressed_bitmap=compressed_bitmap)

    def as_bits(self):
        """
        Bits sequence representation

        Returns
        -------
        str :
            Bits sequence in a string
        """
        return self.header.as_bits() + self.padding.as_bits()

    def as_text(self):
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
    def from_bytes(received, protocol=1):
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
                                  dtag=dtag, w=w, compressed_bitmap=bitmap)
                message.add_padding()
            else:
                bitmap = [i == "1" for i in bitmap]
                message = SCHCAck(rule_id, protocol=protocol, c=c,
                                  dtag=dtag, w=w, compressed_bitmap=bitmap)
        return message
