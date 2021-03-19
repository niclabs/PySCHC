"""rule_id: RuleId Class"""

from math import log
from typing import Tuple
from schc_base import SCHCObject
from schc_protocols import get_protocol


class RuleID(SCHCObject):
    """
    RuleID Class

    Attributes
    ----------
    rule_id : int
        RuleID as an integer
    protocol : SCHCProtocol
        Which protocol it used
    size : int
        Size used by rule_id, in bits
    """

    def __init__(self, rule_id: int, protocol: int = 1) -> None:
        """
        RuleID constructor

        Parameters
        ----------------
        rule_id : int
            RuleID as an integer
        """
        super().__init__()
        self.rule_id = rule_id
        self.protocol = get_protocol(protocol, rule_id=rule_id)
        self.size = self.protocol.RULE_SIZE
        assert log(self.rule_id, 2) + 1 <= self.size, "Rule ID uncodified on this specified protocol"

    def as_bytes(self) -> Tuple[bytes, ...]:
        """
        Returns the bytes representation of the SCHC Header

        Returns
        -------
        Tuple[bytes, ...]:
            Bytes representation of SCHC Header
        """
        if self.protocol.id == 0:
            return self.bits_2_bytes(self.as_bits()),
        elif self.protocol.id == SCHCProtocol.LoRaWAN:
            return self.bits_2_bytes(self.as_bits().zfill(self.protocol.FPORT_LENGTH)),
        else:
            raise NotImplemented("Just LoRaWAN protocol is currently implemented")

    def as_bits(self) -> str:
        """
        Representation of bits sequence

        Returns
        -------
        str :
            Bits sequence as text
        """
        return "{:0b}".format(self.rule_id).zfill(self.protocol.RULE_SIZE)
