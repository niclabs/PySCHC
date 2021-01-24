"""all_1_schc_fragment: All1SCHCFragment Concrete Class"""
from schc_base import SCHCProtocol
from schc_messages import SCHCFragment


class All1SCHCFragment(SCHCFragment):
    """
    Regular SCHC Fragment Class
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
        super().__init__(rule_id, protocol=protocol, dtag=dtag, w=w,
                         fcn=[True] * SCHCProtocol(protocol).N, rcs=rcs)
