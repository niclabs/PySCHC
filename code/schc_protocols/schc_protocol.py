""" schc_protocol: Class with SCHC Protocols"""

from abc import ABC, abstractmethod


class SCHCProtocol(ABC):
    """
    SCHC Protocol specified

    Attributes
    ----------
    RULE_ID : int
        Rule ID value
    RULE_SIZE : int
        Rule size in bits
    L2_WORD : int
        Size of L2 Word in bits (recommended 1 byte = 8 bits)
    T : int
        T value, or DTag size in bits
    M : int
        M value, or W size in bits
    N : int
        N value, or FCN size in bits
    U : int
        U value, or RCS size in bits
    WINDOW_SIZE : int
        Number of Tiles on a window (max)
    TILE_SIZE : int
        Size of Tile in bits
    """

    LoRaWAN = 1
    Sigfox = 2

    def __init__(self, rule_id: int = 0) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id : int, optional
            Specified Rule ID in case Profile is different
        """
        self.id = 0
        self.RULE_ID = rule_id
        self.RULE_SIZE = 0
        self.L2_WORD = 0
        self.T = 0
        self.M = 0
        self.N = 0
        self.U = 0
        self.WINDOW_SIZE = 0
        self.TILE_SIZE = 0

    @abstractmethod
    def set_rule_id(self, rule_id: int) -> None:
        """
        Sets Rule ID changing parameters

        Parameters
        ----------
        rule_id : int
            A valid rule id

        Returns
        -------
        None
            Alter instance
        """
        self.RULE_ID = rule_id
        return
