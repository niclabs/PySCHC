""" schc_null_field: SCHC Null Field Class"""

from schc_messages.schc_header import SCHCField


class SCHCNullField(SCHCField):
    """
    SCHC Null Field Class. Used to implement any header file
    as it is not available

    Attributes
    ----------
    t : int
        0
    m : int
        0
    n : int
        0
    u : int
        0
    window_size : int
        0
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.t = 0
        self.m = 0
        self.n = 0
        self.u = 0
        self.window_size = 0

    def as_bits(self) -> str:
        """
        Represent the field as an empty string

        Returns
        -------
        str :
            An empty string
        """
        return ""
