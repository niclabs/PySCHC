""" schc_protocol: Class with SCHC Protocols"""

from schc_base import SCHCObject


class SCHCProtocol:
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

    def __init__(self, __name__, rule_id=0):
        """
        Constructor

        Parameters
        ----------
        __name__: str
            Protocol name
        rule_id : int, optional
            Specified Rule ID in case Profile is different
        """
        self.__name__ = __name__
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
        self.MAX_ACK_REQUEST = 0
        self.INACTIVITY_TIMER = 0
        self.RETRANSMISSION_TIMER = 0
        return

    def set_rule_id(self, rule_id):
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

    def payload_condition_all1(self, payload):
        """
        Payload on All1 SCHC Fragment is specified in each profile,
        furthermore, this method most be implemented to delete payload
        or remove padding

        Parameters
        ----------
        payload : str
            Payload received as a binary string

        Returns
        -------
        str :
            Payload without padding, or, in case All-1 has not
            payload allowed an empty string
        """
        return ""

    def calculate_rcs(self, packet):
        """
        Calculates RCS according to protocol specification

        Parameters
        ----------
        packet : str
            SCHC Packet as binary string

        Returns
        -------
        str :
            Result of Reassembly Check Sequence (RCS)
        """
        # TODO: self implementation of crc32
        # from binascii import crc32
        # return hex(crc32(SCHCObject.bits_2_bytes(packet)))
        return ""

    def penultimate_tile(self):
        """
        Penultimate tile condition in case Ack-On-Error is used

        Returns
        -------
        int :
            Tile size in bits
        """
        pass
