"""integrity_check: Integrity Check Class"""

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

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        return "{:0b}".format(self.c)
