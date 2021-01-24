"""regular_schc_fragment: Regular SCHCFragment Concrete Class"""
from schc_base import SCHCProtocol, Tile
from schc_messages import SCHCFragment, SCHCMessage


class RegularSCHCFragment(SCHCFragment):
    """
    Regular SCHC Fragment Class

    |-- SCHC Fragment Header -|
             |--T---|-M-|--N--|
    +--------+------+---+-----+------------------+--------------------+
    | RuleID | Dtag | W | FCN | Fragment Payload | padding (as needed)|
    +--------+------+---+-----+------------------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int = 1,
                 dtag: int = None, w: int = None, fcn: int = None) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id
        protocol :
            Optional
        dtag :
            Optional
        w :
            Optional
        fcn :
            Optional
        """
        super().__init__(rule_id, protocol=protocol, dtag=dtag,
                         w=w, fcn=fcn)

    @staticmethod
    def from_bytes(received: bytes, protocol: int = 1) -> SCHCMessage:
        """
        Generate a RegularSCHCFragment instance from bytes

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received, default LoRaWAN

        Returns
        -------
        SCHCMessage :
            An new instance of Regular SCHC Fragment
        """
        protocol_to_use = SCHCProtocol(protocol=protocol)
        bits_received = SCHCMessage.bytes_2_bits(received)
        pointer = protocol_to_use.RULE_SIZE
        rule_id = int(bits_received[0:pointer], 2)
        protocol_to_use = SCHCProtocol(protocol=protocol, rule_id=rule_id)
        dtag = bits_received[pointer:pointer+protocol_to_use.T]
        pointer += protocol_to_use.T
        if dtag == "":
            dtag = None
        else:
            dtag = int(dtag, 2)
        w = bits_received[pointer:pointer+protocol_to_use.M]
        pointer += protocol_to_use.M
        if w == "":
            w = None
        else:
            w = int(w, 2)
        fcn = int(bits_received[pointer:pointer+protocol_to_use.N], 2)
        pointer += protocol_to_use.N
        message = RegularSCHCFragment(rule_id, protocol=protocol,
                                      dtag=dtag, w=w, fcn=fcn)
        payload = bits_received[pointer:]
        if len(payload) % protocol_to_use.L2_WORD > 0:
            padding_size = protocol_to_use.L2_WORD - (len(payload) % protocol_to_use.L2_WORD)
            payload = bits_received[pointer:-padding_size]
        message.add_tile(Tile(SCHCMessage.bits_2_bytes(payload)))
        message.add_padding()
        return message

    def as_bits(self) -> str:
        """
        Bits sequence representation

        Returns
        -------
        str :
            Bits sequence in a string
        """
        return self.header.as_bits() + self.payload.as_bits() + self.padding.as_bits()

    def as_text(self) -> str:
        """
        Writes Regular SCHC Fragment as text

        Returns
        -------
        str :
            Format text
        """
        text_so_far = super().as_text()
        second_header = "|"
        text_tags = "| RuleID "
        content_text = "|{}".format(self.header.rule_id.as_bits())
        space_size = 9
        if len(content_text) >= len(text_tags):
            text_tags += " " * (len(content_text) - len(text_tags)) + "|"
            content_text += "|"
            space_size += len(content_text) - len(text_tags)
        else:
            text_tags += "|"
            content_text += " " * (len(text_tags) - len(content_text)) + "|"
        fields = [
            self.header.dtag,
            self.header.w,
            self.header.fcn
        ]
        conditions = [
            self.header.dtag.t,
            self.header.w.m,
            self.header.fcn.n
        ]
        for condition, field in zip(conditions, fields):
            if condition:
                text_size, tag, content = field.format_text()
                second_header += text_size + "|"
                text_tags += tag + "|"
                content_text += content + "|"
        if self.payload.size >= 18:
            text_tags += " Fragment Payload " + " " * (self.payload.size - 18) + "|"
            content_text += self.payload.as_bits() + "|"
        else:
            text_tags += " Fragment Payload " + "|"
            content_text += self.payload.as_bits() + " " * (18 - self.payload.size) + "|"
        if self.padding.size != 0:
            if self.padding.size >= 9:
                text_tags += " padding " + " " * (self.padding.size - 9) + "|"
                content_text += self.padding.as_bits() + "|"
            else:
                text_tags += " padding " + "|"
                content_text += self.padding.as_bits() + " " * (9 - self.padding.size) + "|"
        if len(second_header) > (30 - space_size):
            text_so_far = text_so_far.format(" " * (len(second_header) - (30 - space_size)))
        else:
            text_so_far = text_so_far.format("")
        return "{}{}\n{}\n{}".format(text_so_far, second_header,
                                     text_tags, content_text)
