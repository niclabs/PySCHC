"""dtag: Datagram Tag Class"""
from typing import Tuple

from schc_messages.schc_header import SCHCField


class DTag(SCHCField):
    """
    Datagram Tag Class

    Attributes
    ----------
    dtag : int
        DTag value as an integer for simplification
    t : int
        Size of Dtag in bits (given according to rule_id)
    """

    def __init__(self, dtag: int, t: int) -> None:
        """
        DTag constructor

        Parameters
        ----------
        dtag : int
            DTag value as an integer for simplification
        t : int
            Size of Dtag in bits (given according to rule_id)
        """
        super().__init__()
        self.dtag = dtag
        self.t = t
        self.size = self.t
        return

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        if self.t == 0:
            return ""
        else:
            return "{:0b}".format(self.dtag).zfill(self.t)

    def format_text(self) -> Tuple[str, str, str]:
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of DTag, as T = {}
        str :
            Name of field: DTag
        content :
            Content in bits
        """
        if self.t != 0:
            text_size = " T={} ".format(self.t)
            content = self.as_bits()
            if len(content) < len(text_size):
                content += " " * (len(text_size) - len(content))
            tag = " DTag " + " " * (len(text_size) - 6)
            return text_size, tag, content
        else:
            return super().format_text()
