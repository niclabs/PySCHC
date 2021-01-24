"""schc_sender_abort: SCHC Sender Abort Class"""

from schc_messages import SCHCMessage


class SCHCSenderAbort(SCHCMessage):
    """
    SCHC Sender Abort Class
    """

    def __init__(self) -> None:
        super().__init__()
