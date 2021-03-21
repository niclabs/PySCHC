"""integrity_check: Integrity Check Class"""
from typing import Tuple

from schc_messages.schc_header import SCHCField


class IntegrityCheck(SCHCField):
    """
    Integrity Check (C) Class

    Attributes
    ----------
    c : bool
        C value as a boolean value
    """

    def __init__(self, c: bool) -> None:
        """
        W constructor

        Parameters
        ----------
        c : bool
            C value as a boolean value
        """
        super().__init__()
        self.c = c
        self.size = 1

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        return "{:0b}".format(self.c)

    def format_text(self) -> Tuple[str, str, str]:
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of C, 1 bit
        str :
            Name of field: C
        content :
            Content in bits
        """
        text_size = " 1 "
        tag = " C "
        content = " {} ".format(self.as_bits())
        return text_size, tag, content
