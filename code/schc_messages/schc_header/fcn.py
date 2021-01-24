"""fcn: Fragment Compressed Number Class"""

from math import log
from typing import Tuple

from schc_messages.schc_header import SCHCField


class FragmentedCompressedNumber(SCHCField):
    """
    Fragmented Compressed Number (FCN) Class

    Attributes
    ----------
    fcn : int
        FCN value as an integer
    n : int
        Size of FCN in bits (given according to rule_id)
    """

    def __init__(self, fcn: int, n: int) -> None:
        """
        W constructor

        Parameters
        ----------
        fcn : int
            FCN value as a boolean list
        n : int
            Size of FCN in bits (given according to rule_id)
        """
        super().__init__()
        assert int(log(63, 2)) + 1 <= n, "FCN must be representable for {} bits".format(n)
        self.fcn = fcn
        self.n = n

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        return "{:0b}".format(self.fcn).zfill(self.n)

    def format_text(self) -> Tuple[str, str, str]:
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of FCN, as N = {}
        str :
            Name of field: FCM
        content :
            Content in bits
        """
        if self.n != 0:
            text_size = "--- N={} ---".format(self.n)
            content = self.as_bits()
            if len(content) < len(text_size):
                content += " " * (len(text_size) - len(content))
            tag = " FCN " + " " * (len(text_size) - 5)
            return text_size, tag, content
        else:
            return super().format_text()
