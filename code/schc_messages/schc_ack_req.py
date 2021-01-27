"""schc_ack_reg: SCHCAckReq Class"""

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

    def __init__(self, rule_id: int, protocol: int = 1,
                 dtag: int = None, w: int = None) -> None:
        super().__init__(rule_id=rule_id, protocol=protocol,
                         dtag=dtag, w=w)
        self.header.fcn = FragmentedCompressedNumber(0, self.protocol.N)
        self.header.size += self.header.fcn.size
        self.size += self.header.fcn.size
        return

    def as_bits(self) -> str:
        """
        Bits sequence representation

        Returns
        -------
        str :
            Bits sequence in a string
        """
        return self.header.as_bits() + self.padding.as_bits()

    def as_text(self) -> str:
        """
        Writes ACK REQ message with specifications

        Returns
        -------
        str :
            SCHC ACK Message as text format
        """
        header_text = "|- SCHC ACK REQ Header {}-|\n"
        return self.base_as_text(header_text)
