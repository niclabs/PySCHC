""" schc_protocol: Class with SCHC Protocols"""


class SCHCProtocol:
    """
    SCHC Protocol specified
    """

    LoRaWAN = 1

    def __init__(self, protocol: int, rule_id: int = 0) -> None:
        """
        Constructor
        Parameters
        ----------
        protocol : int
            SCHC Protocol
        rule_id : int, optional
            Specified Rule ID in case Profile is different

        Raises
        ------
        NotImplemented:
            Any other SCHC protocol, but LoRaWAN
        ValueError:
            Rule ID not defined in protocol
        RuntimeError:
            LoRaWAN cannot support fragmentation of message
        """
        self.id = protocol
        if protocol == 0:
            self.RULE_SIZE = 8  # in bits, placeholder
            self.L2_WORD = 8  # in bits
            if rule_id == 0:
                pass
        elif protocol == self.LoRaWAN:
            self.FPORT_LENGTH = 8  # in bits
            self.RULE_SIZE = 8  # in bits
            self.L2_WORD = 8  # in bits
            if rule_id == 0:
                pass  # To get basic parameters
            elif rule_id == 20:  # Uplink
                self.T = 0  # in bits
                self.M = 2  # in bits
                self.N = 6  # in bits
                self.U = 32  # in bits
                self.WINDOW_SIZE = 63  # 2^(n=6) = 64 - {All-1 fragment}
                self.TILE_SIZE = 10 * 8  # 10 bytes = 80 bits
            elif rule_id == 21:  # Downlink
                self.T = 0  # in bits
                self.M = 1  # in bits
                self.N = 1  # in bits
                self.U = 32  # in bits
                self.WINDOW_SIZE = 1  # 2^(n=1) = 2 - {All-1 fragment}
                self.TILE_SIZE = 0  # undefined __a priori__
            elif rule_id == 22:
                raise RuntimeError("Cannot fragment message under LoRaWAN protocol")
            else:
                raise ValueError("Rule ID not defined in protocol")
        else:
            NotImplemented("Just LoRaWAN protocol is currently implemented")
