"""schc_receiver_abort: SCHC Receiver Abort Class"""

from schc_messages import SCHCMessage


class SCHCReceiverAbort(SCHCMessage):
    """
    SCHC Receiver Abort Class
    """

    def __init__(self) -> None:
        super().__init__()
