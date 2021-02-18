"""schc_sender_abort: SCHC Sender Abort Class"""

from schc_messages import SCHCMessage
from schc_messages.schc_header import FragmentedCompressedNumber


class SCHCSenderAbort(SCHCMessage):
    """
    SCHC Sender Abort Class

     |--- Sender Abort Header ---|
             |--T---|-M-|-- N  --|
    +--------+------+---+--------+--------------------+
    | RuleID | Dtag | W | 1...1  | padding (as needed)|
    +--------+------+---+--------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int = 1,
                 dtag: int = None, w: int = None) -> None:
        super().__init__(rule_id=rule_id, protocol=protocol,
                         dtag=dtag, w=w)
        self.header.fcn = FragmentedCompressedNumber(int(2**self.protocol.N) - 1,
                                                     self.protocol.N)
        self.header.size += self.header.fcn.size
        self.size += self.header.fcn.size
        if self.header.w.size != 0:
            self.header.w.w = int(2**self.header.w.size) - 1
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
        Writes Sender Abort message with specifications

        Returns
        -------
        str :
            SCHC Sender Abort Message as text format
        """
        header_text = "|- Sender-Abort Header {}-|\n"
        return self.base_as_text(header_text)

    @staticmethod
    def from_bytes(received: bytes, protocol: int = 1) -> SCHCMessage:
        """
        Generates a SCHC Sender Abort instance from bytes

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received, default LoRaWAN

        Returns
        -------
        SCHCMessage :
            An new instance of SCHC Sender Abort
        """
        protocol_to_use, bits_received, pointer, rule_id, dtag, w = SCHCSenderAbort._get_common_(
            received, protocol=protocol)
        return SCHCSenderAbort(rule_id, protocol=protocol_to_use.id,
                               dtag=dtag, w=w)
