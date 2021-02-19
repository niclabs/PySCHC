"""schc_header: SCHC Header Class"""

from schc_base import SCHCObject
from schc_protocols import get_protocol
from schc_messages.schc_header import SCHCField, SCHCNullField
from schc_messages.schc_header import RuleID, DTag, WField, FragmentedCompressedNumber
from schc_messages.schc_header import ReassemblyCheckSequence, IntegrityCheck, CompressedBitmap


class SCHCHeader(SCHCObject):
    """
    SCHC Header Class

    Attributes
    ----------
    rule_id : RuleID
        Rule ID
    protocol : SCHCProtocol
        Protocol object
    dtag : SCHCField
        A DTag object or SCHCNullObject
    w : SCHCField
        A WField object or SCHCNullObject
    fcn : SCHCField
        A FragmentedCompressedNumber object or SCHCNullObject
    rcs : SCHCField
        A ReassemblyCheckSequence object or SCHCNullObject
    c : SCHCField
        A IntegrityCheck object or SCHCNullObject
    compressed_bitmap : SCHCField
        A CompressedBitmap object or SCHCNullObject
    size
    """

    def __init__(self, rule_id: int, protocol: int = 1, **kwargs) -> None:
        """
        SCHC Header constructor

        Parameters
        ----------
        rule_id : int
            RuleID of SCHC Message
        protocol : int
            SCHC Protocol

        Other Parameters
        ----------------
        dtag : DTag, optional
            Datagram Tag field
        w : int, optional
            Presented if windows are used. Identifies a window
        fcn : int, optional
            Information about the progress in the sequence of tiles being transmitted,
            specifically the first tile in sequence
        rcs : str, optional
            RCS computation result
        c : bool or None, optional
            Whether or not the integrity check was successful
        bitmap : List[bool], optional
            To report on the receiver bitmap
        """
        super().__init__()
        self.rule_id = RuleID(rule_id, protocol=protocol)
        self.protocol = get_protocol(protocol, rule_id=rule_id)
        self.dtag = SCHCNullField()
        self.w = SCHCNullField()
        self.fcn = SCHCNullField()
        self.rcs = SCHCNullField()
        self.c = SCHCNullField()
        self.compressed_bitmap = SCHCNullField()
        if kwargs.get("dtag", None) is not None:
            self.dtag = DTag(kwargs.get("dtag"), self.protocol.T)
        if kwargs.get("w", None) is not None:
            self.w = WField(kwargs.get("w"), self.protocol.M)
        if kwargs.get("fcn", None) is not None:
            self.fcn = FragmentedCompressedNumber(kwargs.get("fcn"), self.protocol.N)
        if kwargs.get("rcs", None) is not None:
            self.rcs = ReassemblyCheckSequence(kwargs.get("rcs"), self.protocol.U)
        if kwargs.get("c", None) is not None:
            self.c = IntegrityCheck(kwargs.get("c"))
        if kwargs.get("bitmap", None) is not None:
            self.compressed_bitmap = CompressedBitmap(kwargs.get("bitmap"), self.protocol.WINDOW_SIZE)
        self.size = sum([
            self.rule_id.size, self.dtag.t, self.w.m,
            self.fcn.n, self.rcs.u, len(self.c.as_bits()),
            self.compressed_bitmap.window_size
        ])

    def as_bits(self) -> str:
        """
        Representation of bits sequence

        Returns
        -------
        str :
            Bits sequence as text
        """
        return ''.join([
            self.rule_id.as_bits(),
            self.dtag.as_bits(),
            self.w.as_bits(),
            self.fcn.as_bits(),
            self.rcs.as_bits(),
            self.c.as_bits(),
            self.compressed_bitmap.as_bits(),
        ])
