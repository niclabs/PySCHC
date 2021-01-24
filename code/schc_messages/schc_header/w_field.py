"""w_field: W Class"""
from typing import Tuple

from schc_messages.schc_header import SCHCField


class WField(SCHCField):
    """
    W Class

    Attributes
    ----------
    w : int
        W value as an integer for simplification
    m : int
        Size of W in bits (given according to rule_id)
    """

    def __init__(self, w: int, m: int) -> None:
        """
        W constructor

        Parameters
        ----------
        w : int
            W value as an integer for simplification
        m : int
            Size of W in bits (given according to rule_id)
        """
        super().__init__()
        self.w = w
        self.m = m

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        return "{:0b}".format(self.w).zfill(self.m)

    def format_text(self) -> Tuple[str, str, str]:
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of W, as M = {}
        str :
            Name of field: W
        content :
            Content in bits
        """
        if self.w != 0:
            text_size = "-- M={} --".format(self.m)
            content = self.as_bits()
            if len(content) < len(text_size):
                content += " " * (len(text_size) - len(content))
            tag = " W " + " " * (len(text_size) - 3)
            return text_size, tag, content
        else:
            return super().format_text()
