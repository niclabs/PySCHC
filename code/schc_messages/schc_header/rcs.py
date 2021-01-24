"""rcs: Reassembly Check Sequence Class"""

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

    def as_bits(self) -> str:
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        return "{:0b}".format(int(self.rcs)).zfill(self.u)
