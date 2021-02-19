"""regular_schc_fragment: Regular SCHCFragment Concrete Class"""

from schc_base import Tile
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
        Generates a RegularSCHCFragment instance from bytes

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
        protocol_to_use, bits_received, pointer, rule_id, dtag, w = RegularSCHCFragment._get_common_(received, protocol=protocol)
        fcn = int(bits_received[pointer:pointer+protocol_to_use.N], 2)
        pointer += protocol_to_use.N
        message = RegularSCHCFragment(rule_id, protocol=protocol,
                                      dtag=dtag, w=w, fcn=fcn)
        payload = bits_received[pointer:]
        tile_size = protocol_to_use.TILE_SIZE
        if tile_size == 0:
            tile_size = 8
        if len(payload) % tile_size > 0:
            padding_size = len(payload) % tile_size
            payload = payload[0:-padding_size]
        message.add_tile(Tile(SCHCMessage.bits_2_bytes(payload)))
        message.add_padding()
        return message
