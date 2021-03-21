"""compressed_bitmap: Compressed Bitmap Class"""

from typing import List, Tuple
from schc_messages.schc_header import SCHCField


class CompressedBitmap(SCHCField):
    """
    Compressed Bitmap Class

    Attributes
    ----------
    bitmap : List[bool]
        Bitmap of tile send in a window
    window_size : int
        WINDOW SIZE given on initialization
    """

    def __init__(self, bitmap: List[bool], window_size: int) -> None:
        """
        Compressed Bitmap constructor

        Parameters
        ----------
        bitmap : List[bool]
            Bitmap, it has to have a length of at most window size
        window_size : int
            Size of window
        """
        super().__init__()
        assert len(bitmap) <= window_size, "You cannot specified more bitmap than windows"
        self.bitmap = bitmap
        self.window_size = window_size
        self.size = len(bitmap)
        return

    def as_bits(self) -> str:
        """
        Returns the bytes representation of the SCHC Header

        Returns
        -------
        str :
            String with bit representation
        """
        out = ""
        for bit in self.bitmap:
            if bit:
                out += "1"
            else:
                out += "0"
        return out

    def format_text(self) -> Tuple[str, str, str]:
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of Compressed bitmap, this can be before of after compression
        str :
            Name of field: Compressed Bitmap
        content :
            Content in bits
        """
        if self.size != 0:
            content = self.as_bits()
            if len(content) >= 19:
                tag = " Compressed Bitmap " + " " * (len(content) - 19)
            else:
                tag = " Compressed Bitmap "
                content += " " * (19 - len(content))
            return "", tag, content
        else:
            return super().format_text()
