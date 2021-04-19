"""rule_id: RuleId Class"""

from math import log
from schc_base import SCHCObject
from schc_protocols import get_protocol, SCHCProtocol


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

    def __init__(self, rule_id, protocol=1):
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

    def as_bytes(self):
        """
        Returns the bytes representation of the SCHC Header

        Returns
        -------
        bytes:
            Bytes representation of SCHC Header
        """
        if self.protocol.id == 0:
            return self.bits_2_bytes(self.as_bits())
        elif self.protocol.id == SCHCProtocol.LoRaWAN:
            return self.bits_2_bytes(self.zfill(self.as_bits(), self.protocol.FPORT_LENGTH))
        else:
            raise NotImplemented("Just LoRaWAN protocol is currently implemented")

    def as_bits(self):
        """
        Representation of bits sequence

        Returns
        -------
        str :
            Bits sequence as text
        """
        return self.zfill("{:0b}".format(self.rule_id), self.protocol.RULE_SIZE)
