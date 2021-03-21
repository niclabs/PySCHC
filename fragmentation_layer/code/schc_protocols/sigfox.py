""" sigfox: Sigfox implementation Protocol """

from schc_protocols import SCHCProtocol
from warnings import warn


class Sigfox(SCHCProtocol):
    """
    Sigfox Protocol Class
    """
    def __init__(self, rule_id: int = 0) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id : int, optional
            Specified Rule ID in case Profile is different
        """
        super().__init__("Sigfox", rule_id)
        warn("Sigfox is added for testing and completeness, but it is not implemented yet",
             ImportWarning)
        self.id = 2  # Numeral key of Sigfox

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
            Sigfox cannot support fragmentation of message
        """
        super().set_rule_id(rule_id)
        return

    def payload_condition_all1(self, payload: str) -> str:
        """
        Pending...

        Parameters
        ----------
        payload : str
            Payload received as a binary string

        Returns
        -------
        str :
            Pending...
        """
        return ""

    def calculate_rcs(self, packet: str) -> str:
        """
        Pending

        Parameters
        ----------
        packet : str
            SCHC Packet as binary string

        Returns
        -------
        str :
            Pending...
        """
        return ""

    def penultimate_tile(self) -> int:
        """
        Pending...

        Returns
        -------
        int :
            Pending ...
        """
        return 0
