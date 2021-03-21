"""schc_receiver_abort: SCHC Receiver Abort Class"""

from schc_messages import SCHCMessage
from schc_messages.schc_header import IntegrityCheck


class SCHCReceiverAbort(SCHCMessage):
    """
    SCHC Receiver Abort Class

     |--- Sender Abort Header ---|
             |--T---|-M-|-- N  --|
    +--------+------+---+--------+--------------------+
    | RuleID | Dtag | W | 1...1  | padding (as needed)|
    +--------+------+---+--------+--------------------+

    Attributes
    ----------
    ones : int
        Ones to add
    """

    def __init__(self, rule_id: int, protocol: int = 1,
                 dtag: int = None, w: int = None) -> None:
        super().__init__(rule_id=rule_id, protocol=protocol,
                         dtag=dtag, w=w)
        if self.header.w.size != 0:
            self.header.w.w = int(2**self.header.w.size) - 1
        self.header.c = IntegrityCheck(True)
        self.header.size += 1
        self.size += 1
        self.ones = 0
        self.__fill_ones__()
        return

    def as_bits(self) -> str:
        """
        Bits sequence representation

        Returns
        -------
        str :
            Bits sequence in a string
        """
        return self.header.as_bits() + ("1" * self.ones)

    def add_padding(self) -> int:
        """
        Do nothing, method not allowed

        Warnings
        --------
        RuntimeWarning
            Padding cannot be added to Receiver Abort

        Returns
        -------
        int :
            0
        """
        from warnings import warn
        warn("Padding cannot be added to Receiver Abort",
             RuntimeWarning)
        return 0

    def as_text(self) -> str:
        """
        Writes Sender Abort message with specifications

        Returns
        -------
        str :
            SCHC Sender Abort Message as text format
        """
        header_text = "| Receiver-Abort Header{}|\n"
        text = self.base_as_text(header_text)
        if self.ones > self.protocol.L2_WORD:
            ones = "1" * (self.ones - self.protocol.L2_WORD)
            ones += "|"
            ones += "1" * self.protocol.L2_WORD
        else:
            ones = self.ones * "1"
        return text + ones + "|"

    def __fill_ones__(self) -> None:
        """
        Fills one according to RFC8724

        Returns
        -------
        Alter instance (attributes: size and ones)
        """
        if self.ones != 0:
            from warnings import warn
            warn("Ones can be added just once",
                 RuntimeWarning)
            return
        last_word_size = self.size % self.protocol.L2_WORD
        if last_word_size != 0:
            self.ones = self.protocol.L2_WORD - last_word_size
        self.ones += self.protocol.L2_WORD
        self.size += self.ones
        return

    @staticmethod
    def from_bytes(received: bytes, protocol: int = 1) -> SCHCMessage:
        """
        Generates a SCHC Receiver Abort instance from bytes

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received, default LoRaWAN

        Returns
        -------
        SCHCMessage :
            An new instance of SCHC Receiver Abort
        """
        protocol_to_use, bits_received, pointer, rule_id, dtag, w = SCHCReceiverAbort._get_common_(
            received, protocol=protocol)
        assert "{:0b}".format(w) == "1" * protocol_to_use.M,\
            "W != {}, must be all-1, Receiver Abort must be ignored".format("{:0b}".format(w))
        c = bits_received[pointer:pointer+1] == "1"
        assert c, "C = 0, Receiver Abort must be ignored"
        pointer += 1
        padding = bits_received[pointer:]
        padding_length = protocol_to_use.L2_WORD - (sum(
            [protocol_to_use.RULE_SIZE, protocol_to_use.T,
             protocol_to_use.M, 1]) % protocol_to_use.L2_WORD)
        padding_length += protocol_to_use.L2_WORD
        assert padding == "1" * padding_length,\
            "Ones padding must be {}, got {}, Abort must be ignored".format(
                "1" * padding_length,
                padding
            )
        return SCHCReceiverAbort(rule_id, protocol=protocol_to_use.id,
                                 dtag=dtag, w=w)
