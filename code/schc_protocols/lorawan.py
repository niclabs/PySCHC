""" lorawan: LoRaWAN implementation Protocol """

from schc_protocols import SCHCProtocol


class LoRaWAN(SCHCProtocol):
    """
    LoRaWAN Protocol Class
    """
    UPLINK = 20
    DOWNLINK = 21
    NOT_POSSIBLE = 22

    def __init__(self, rule_id: int = 0) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id : int, optional
            Specified Rule ID in case Profile is different

        Raises
        ------
        ValueError:
            Rule ID not defined in protocol
        RuntimeError:
            LoRaWAN cannot support fragmentation
        """
        super().__init__("LoRaWAN", rule_id)
        self.id = 1  # Numeral key of LoRaWAN
        self.FPORT_LENGTH = 8  # in bits
        self.RULE_SIZE = 8  # in bits
        self.L2_WORD = 8  # in bits
        self.__set_parameters__()

    def set_rule_id(self, rule_id: int) -> None:
        """
        Sets Rule ID

        Parameters
        ----------
        rule_id : int
            A valid rule id for protocol

        Returns
        -------
        None

        Raises
        ------
        ValueError:
            Rule ID not defined in protocol
        RuntimeError:
            LoRaWAN cannot support fragmentation of message
        """
        super().set_rule_id(rule_id)
        self.__set_parameters__()
        return

    def __set_parameters__(self) -> None:
        if self.RULE_ID == 0:
            pass  # To get basic parameters
        elif self.RULE_ID == LoRaWAN.UPLINK:  # Uplink
            self.T = 0  # in bits
            self.M = 2  # in bits
            self.N = 6  # in bits
            self.U = 32  # in bits
            self.WINDOW_SIZE = 63  # 2^(n=6) = 64 - {All-1 fragment}
            self.TILE_SIZE = 10 * 8  # 10 bytes = 80 bits
            self.MAX_ACK_REQUEST = 1e6  # TODO
            self.INACTIVITY_TIMER = 10  # in seconds TODO
            self.RETRANSMISSION_TIMER = 10  # in seconds TODO
        elif self.RULE_ID == LoRaWAN.DOWNLINK:  # Downlink
            self.T = 0  # in bits
            self.M = 1  # in bits
            self.N = 1  # in bits
            self.U = 32  # in bits
            self.WINDOW_SIZE = 1  # 2^(n=1) = 2 - {All-1 fragment}
            self.TILE_SIZE = 0  # undefined __a priori__
            self.MAX_ACK_REQUEST = 8
            self.INACTIVITY_TIMER = 12 * 60 * 60  # in seconds (12 hours)
            self.RETRANSMISSION_TIMER = 30  # in seconds
        elif self.RULE_ID == LoRaWAN.NOT_POSSIBLE:
            raise RuntimeError("Cannot fragment message under LoRaWAN protocol")
        else:
            raise ValueError("Rule ID not defined in protocol")
        return

    def payload_condition_all1(self, payload: str) -> str:
        """
        Just one tile is allowed

        payload : str
            Payload received as a binary string

        Returns
        -------
        str :
            Payload without padding
        """
        if payload == "":
            return ""
        else:
            if self.RULE_ID == LoRaWAN.UPLINK:
                return payload[0: self.TILE_SIZE]
            elif self.RULE_ID == LoRaWAN.DOWNLINK:
                return payload

    def calculate_rcs(self, packet: str) -> str:
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
        return super().calculate_rcs(packet)

    def penultimate_tile(self) -> int:
        """
        Same as regular tiles

        Returns
        -------
        int :
            Same as tile size on uplink (none on downlink)
        """
        if self.RULE_ID == LoRaWAN.UPLINK:
            return self.TILE_SIZE
        else:
            return 0
