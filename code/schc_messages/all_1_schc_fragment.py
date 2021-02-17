"""all_1_schc_fragment: All1SCHCFragment Concrete Class"""

from schc_messages import SCHCFragment
from schc_messages.schc_header import FragmentedCompressedNumber


class All1SCHCFragment(SCHCFragment):
    """
    Regular SCHC Fragment Class

    |---- SCHC Fragment Header -----|
             |--T---|-M-|--N--|--U--|
    +--------+------+---+-----+-----+------------------+--------------------+
    | RuleID | Dtag | W | FCN | RCS | Fragment Payload | padding (as needed)|
    +--------+------+---+-----+-----+------------------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int = 1, dtag: int = None,
                 w: int = None, rcs: str = None) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id
        protocol :
            Optional
        dtag :
            Optional
        w :
            Optional
        rcs :
            Optional
        """
        super().__init__(rule_id, protocol=protocol, dtag=dtag, w=w, rcs=rcs)
        self.header.fcn = FragmentedCompressedNumber(int(2**self.protocol.N) - 1,
                                                     self.protocol.N)
        self.header.size += self.header.fcn.size
        self.size += self.header.fcn.size
        return
