"""rcs: Reassembly Check Sequence Class"""
from typing import Tuple

from schc_messages.schc_header import SCHCField


class ReassemblyCheckSequence(SCHCField):
    """
    Reassembly Check Sequence (RCS) Class

    Attributes
    ----------
    rcs : str
        RCS value as a string
    u : int
        Size of RCS in bits (given according to rule_id)
    """

    def __init__(self, rcs: str, u: int) -> None:
        """
        RCS constructor

        Parameters
        ----------
        rcs : str
            RCS value as an integer for simplification
        u : int
            Size of RCS in bits (given according to rule_id)
        """
        super().__init__()
        self.rcs = rcs
        self.u = u
        self.size = self.u
        return

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        rcs = int(self.rcs, 0)
        return "{:0b}".format(rcs).zfill(self.u)

    def format_text(self) -> Tuple[str, str, str]:
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of rcs, as U = {}
        str :
            Name of field: RCS
        content :
            Content in bits
        """
        if self.u != 0:
            text_size = " U={} ".format(self.u)
            content = self.as_bits()
            if len(content) < len(text_size):
                content += " " * (len(text_size) - len(content))
            else:
                text_size += " " * (len(content) - len(text_size))
            tag = " RCS " + " " * (len(text_size) - 5)
            return text_size, tag, content
        else:
            return super().format_text()
