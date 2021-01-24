"""compressed_bitmap: Compressed Bitmap Class"""

from typing import List
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
        if len(bitmap) < window_size:
            from warnings import warn
            warn("Bitmap has less values than windows, this will fill the not specified ones with False",
                 UserWarning)
        self.bitmap = bitmap
        self.window_size = window_size
        for _ in range(self.window_size - len(self.bitmap)):
            self.bitmap.append(False)

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
