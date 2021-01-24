"""schc_padding: SCHC Padding Class"""
from typing import Tuple

from schc_base import SCHCObject


class SCHCPadding(SCHCObject):
    """
    SCHC Padding Class
    """

    def __init__(self) -> None:
        super().__init__()

    def add(self, size: int) -> int:
        """
        Add bits to padding

        Parameters
        ----------
        size : int
            Size to add to padding

        Returns
        -------
        int :
            Current size of padding
        """
        self.size += size
        return self.size

    def as_bits(self) -> str:
        """
        Bit by bit representation

        Returns
        -------
        str :
            A str with just '0'
        """
        return '0' * self.size
