"""regular_schc_fragment: Regular SCHCFragment Concrete Class"""
from schc_base import Tile
from schc_protocols import get_protocol
from schc_messages import SCHCFragment, SCHCMessage


class RegularSCHCFragment(SCHCFragment):
    """
    Regular SCHC Fragment Class

    |-- SCHC Fragment Header -|
             |--T---|-M-|--N--|
    +--------+------+---+-----+------------------+--------------------+
    | RuleID | Dtag | W | FCN | Fragment Payload | padding (as needed)|
    +--------+------+---+-----+------------------+--------------------+
    """

    def __init__(self, rule_id: int, protocol: int = 1,
                 dtag: int = None, w: int = None, fcn: int = None) -> None:
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
        fcn :
            Optional
        """
        super().__init__(rule_id, protocol=protocol, dtag=dtag,
                         w=w, fcn=fcn)

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
        protocol_to_use = get_protocol(protocol)
        bits_received = SCHCMessage.bytes_2_bits(received)
        pointer = protocol_to_use.RULE_SIZE
        rule_id = int(bits_received[0:pointer], 2)
        protocol_to_use.set_rule_id(rule_id=rule_id)
        dtag = bits_received[pointer:pointer+protocol_to_use.T]
        pointer += protocol_to_use.T
        if dtag == "":
            dtag = None
        else:
            dtag = int(dtag, 2)
        w = bits_received[pointer:pointer+protocol_to_use.M]
        pointer += protocol_to_use.M
        if w == "":
            w = None
        else:
            w = int(w, 2)
        fcn = int(bits_received[pointer:pointer+protocol_to_use.N], 2)
        pointer += protocol_to_use.N
        message = RegularSCHCFragment(rule_id, protocol=protocol,
                                      dtag=dtag, w=w, fcn=fcn)
        payload = bits_received[pointer:]
        if len(payload) % protocol_to_use.L2_WORD > 0:
            padding_size = protocol_to_use.L2_WORD - (len(payload) % protocol_to_use.L2_WORD)
            payload = bits_received[pointer:-padding_size]
        message.add_tile(Tile(SCHCMessage.bits_2_bytes(payload)))
        message.add_padding()
        return message
