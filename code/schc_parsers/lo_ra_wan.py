""" lo_ra_wan: LoRaWAN parser function """

from schc_messages import SCHCMessage, SCHCAck
from schc_protocols import LoRaWAN


def parse(message: bytes) -> SCHCMessage:
    """
    Parses message receive according to LoRaWAN Profile

    Parameters
    ----------
    message : bytes
        Bytes received

    Returns
    -------
    SCHCMessage :
        SCHCMessage with attributes given by content received
    """
    protocol_to_use = LoRaWAN()
    bits_received = SCHCMessage.bytes_2_bits(message)
    pointer = protocol_to_use.RULE_SIZE
    rule_id = int(bits_received[0:pointer], 2)
    protocol_to_use.set_rule_id(rule_id)
    header_min_size = protocol_to_use.RULE_SIZE + protocol_to_use.T + protocol_to_use.M
    if len(bits_received) == header_min_size + (header_min_size % protocol_to_use.TILE_SIZE):
        return SCHCAck.from_bytes(message)
    else:
        fcn = bits_received[header_min_size:header_min_size + protocol_to_use.N]
        print(fcn)
    return
