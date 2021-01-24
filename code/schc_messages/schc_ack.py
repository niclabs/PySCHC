"""schc_ack: SCHCAck Class"""
from typing import List

from schc_messages import SCHCMessage


class SCHCAck(SCHCMessage):
    """
    SCHC Ack Class
    """

    def __init__(self, rule_id: int, c: bool, protocol: int = 1, dtag: int = None,
                 w: int = None, bitmap_compressed: List[bool] = None) -> None:
        assert (w is None or c) or bitmap_compressed is not None,\
            "If windows are used and c is True, bitmap must be specified"
        super().__init__(rule_id=rule_id, protocol=protocol, dtag=dtag,
                         w=w, c=c, bitmap_compressed=None if c else bitmap_compressed)
