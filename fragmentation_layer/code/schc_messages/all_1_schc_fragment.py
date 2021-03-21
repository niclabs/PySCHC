"""all_1_schc_fragment: All1SCHCFragment Concrete Class"""

from schc_base import Tile
from schc_messages import SCHCFragment, SCHCMessage
from schc_messages.schc_header import FragmentedCompressedNumber


class All1SCHCFragment(SCHCFragment):
    """
    Regular SCHC Fragment Class

    |---- SCHC Fragment Header -----|
             |--T---|-M-|--N--|--U--|
    +--------+------+---+-----+-----+------------------+--------------------+
    | RuleID | Dtag | W | FCN | RCS | Fragment Payload | padding (as needed)|
    +--------+------+---+-----+-----+------------------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int = 1, dtag: int = None,
                 w: int = None, rcs: str = None) -> None:
        """
        Constructor

        Parameters
        ----------
        rule_id
        protocol :
            Optional
        dtag :
            Optional
        w :
            Optional
        rcs :
            Optional
        """
        super().__init__(rule_id, protocol=protocol, dtag=dtag, w=w, rcs=rcs)
        self.header.fcn = FragmentedCompressedNumber(int(2**self.protocol.N) - 1,
                                                     self.protocol.N)
        self.header.size += self.header.fcn.size
        self.size += self.header.fcn.size
        return

    @staticmethod
    def from_bytes(received: bytes, protocol: int = 1) -> SCHCMessage:
        """
        Generate a RegularSCHCFragment instance from bytes

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received, default LoRaWAN

        Returns
        -------
        SCHCMessage :
            An new instance of Regular SCHC Fragment
        """
        protocol_to_use, bits_received, pointer, rule_id, dtag, w = All1SCHCFragment._get_common_(
            received, protocol=protocol)
        fcn = bits_received[pointer:pointer+protocol_to_use.N]
        assert fcn == "1" * protocol_to_use.N, "FCN not all-1 in an All-1 SCHC Fragment"
        pointer += protocol_to_use.N
        rcs = hex(int(bits_received[pointer:pointer+protocol_to_use.U], 2))
        message = All1SCHCFragment(rule_id, protocol=protocol,
                                   dtag=dtag, w=w, rcs=rcs)
        pointer += protocol_to_use.U
        payload = bits_received[pointer:]
        payload = protocol_to_use.payload_condition_all1(payload)
        if len(payload) != 0:
            message.add_tile(Tile(SCHCMessage.bits_2_bytes(payload)))
            message.add_padding()
        return message
