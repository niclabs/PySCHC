"""tile: Tile class representation"""
from typing import Tuple

from schc_base import SCHCObject


class Tile(SCHCObject):
    """
    Tile Class, to encapsulate basic unit of SCHC

    Attributes
    ----------
    content : bytes
        Content of tile
    size : int
        Size in bit
    """

    def __init__(self, content: bytes):
        """

        Parameters
        ----------
        content
        """
        super().__init__()
        self.content = content
        self.size = len(content) * 8

    def as_bytes(self) -> Tuple[bytes, ...]:
        """
        Byte representation of tile

        Returns
        -------
        Tuple[bytes]:
            A tuple (of length 0) containing the content of Tile
        """
        return self.content,

    def as_bits(self) -> str:
        """
        Representation of bits sequence

        Returns
        -------
        str :
            Bits sequence as text
        """
        return self.bytes_2_bits(self.content)
