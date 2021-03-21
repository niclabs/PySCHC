"""tile: Tile class representation"""

from typing import Tuple, Union
from schc_base import SCHCObject


class Tile(SCHCObject):
    """
    Tile Class, to encapsulate basic unit of SCHC

    Attributes
    ----------
    content : bytes
        Content of tile
    encoded_content : bits
        Content as a string of 0s and 1s
    size : int
        Size in bit
    """

    def __init__(self, content: Union[bytes, str]) -> None:
        """

        Parameters
        ----------
        content : bytes or str
            Tile must contain bytes or be a binary string
        """
        super().__init__()
        if isinstance(content, bytes):
            self.content = content
            self.encoded_content = SCHCObject.bytes_2_bits(content)
        elif isinstance(content, str):
            unique_chars = list(set(content))
            if len(unique_chars) != 2 or not ("0" in unique_chars and "1" in unique_chars):
                raise TypeError("content must be a binary string (just 0s and 1s are allowed)")
            self.encoded_content = content
            self.content = SCHCObject.bits_2_bytes(content)
        else:
            raise TypeError("content must be bytes or a string of 0s and 1s")
        self.size = len(self.encoded_content)
        return

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
        return self.encoded_content
