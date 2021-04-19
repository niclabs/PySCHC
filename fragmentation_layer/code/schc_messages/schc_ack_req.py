"""schc_ack_req: SCHCAckReq Class"""

from schc_messages import SCHCMessage
from schc_messages.schc_header import FragmentedCompressedNumber


class SCHCAckReq(SCHCMessage):
    """
    SCHC Ack REQ Class

    |---- SCHC ACK REQ Header ---|
             |--T---|-M-|-- N --|
    +--------+------+---+-------+--------------------+
    | RuleID | Dtag | W | 0...0 | padding (as needed)|
    +--------+------+---+-------+--------------------+
    """

    def __init__(self, rule_id, protocol=1, dtag=None, w=None):
        super().__init__(rule_id=rule_id, protocol=protocol,
                         dtag=dtag, w=w)
        self.header.fcn = FragmentedCompressedNumber(0, self.protocol.N)
        self.header.size += self.header.fcn.size
        self.size += self.header.fcn.size
        return

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
        Writes ACK REQ message with specifications

        Returns
        -------
        str :
            SCHC ACK Message as text format
        """
        header_text = "|- SCHC ACK REQ Header {}-|\n"
        return self.base_as_text(header_text)

    @staticmethod
    def from_bytes(received, protocol=1):
        """
        Generates a SCHCAckReq instance from bytes

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received, default LoRaWAN

        Returns
        -------
        SCHCMessage :
            An new instance of SCHC Ack Req
        """
        protocol_to_use, bits_received, pointer, rule_id, dtag, w = SCHCAckReq._get_common_(received, protocol=protocol)
        fcn = bits_received[pointer:pointer+protocol_to_use.N]
        assert fcn == "0" * protocol_to_use.N, "FCN not all-0 in an SCHC Ack Req"
        message = SCHCAckReq(rule_id, protocol=protocol,
                             dtag=dtag, w=w)
        message.add_padding()
        return message
