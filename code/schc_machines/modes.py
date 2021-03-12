""" modes: Define modes for logging"""


class AckOnError:
    """
    Ack On Error Mode
    """
    __mode__ = "Ack-On-Error"


class AckAlways:
    """
    Ack Always Mode
    """
    __mode__ = "Ack-Always"


class NoAck:
    """
    No Ack Mode
    """
    __mode__ = "No-Ack"
