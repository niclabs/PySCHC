"""schc_ack_reg: SCHCAckReq Class"""

from schc_messages import SCHCMessage


class SCHCAckReq(SCHCMessage):
    """
    SCHC Ack REQ Class
    """

    def __init__(self) -> None:
        super().__init__()
