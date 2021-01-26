"""schc_fragment: SCHCFragment Class"""

from abc import ABC, abstractmethod
from schc_base import Tile
from schc_messages import SCHCMessage


class SCHCFragment(SCHCMessage, ABC):
    """
    SCHC Fragment Abstract Class

    |-- SCHC Fragment Header -|
    +--------+------+---+-----+------------------+--------------------+
    | RuleID | Dtag | W | ··· | Fragment Payload | padding (as needed)|
    +--------+------+---+-----+------------------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int = 1, dtag: int = None,
                 w: int = None, fcn: int = None, rcs: str = None) -> None:
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
        rcs :
            Optional

        See Also
        --------
        schc_message.schc_header.schc_header.SCHCHeader :
            Description of Other Parameters
        """
        super().__init__(rule_id=rule_id, protocol=protocol, dtag=dtag,
                         w=w, fcn=fcn, rcs=rcs)

    def add_tile(self, tile: Tile) -> int:
        """
        Adds tile to payload of message

        Parameters
        ----------
        tile : Tile
            A tile to add to payload

        Returns
        -------
        int :
            Size of current SCHC Fragment
        """
        payload_size = self.payload.add_content(tile.as_bits())
        self.size = self.header.size + payload_size + self.padding.size
        return self.size

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
        Writes message with specifications

        Returns
        -------
        str :
            SCHC Message as text format
        """
        header_text = "|--- SCHC Fragment Header {}---|\n"
        second_header = " " * (max(len(self.header.rule_id.as_bits()), 8) + 1) + "|"
        text_tags = "| RuleID "
        content_text = "|{}".format(self.header.rule_id.as_bits())
        if len(content_text) >= len(text_tags):
            text_tags += " " * (len(content_text) - len(text_tags)) + "|"
            content_text += "|"
        else:
            text_tags += "|"
            content_text += " " * (len(text_tags) - len(content_text)) + "|"
        fields = [
            self.header.dtag,
            self.header.w,
            self.header.fcn,
            self.header.rcs,
        ]
        for field in fields:
            if field.size != 0:
                text_size, tag, content = field.format_text()
                second_header += text_size + "|"
                text_tags += tag + "|"
                content_text += content + "|"
        if len(second_header) > 30:
            header_text = header_text.format(" " * (len(second_header) - 30))
        else:
            header_text = header_text.format("")
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
        return "{}{}\n{}\n{}".format(header_text, second_header,
                                     text_tags, content_text)

