""" lorawan: LoRaWAN parser function """

from schc_messages import SCHCMessage, SCHCAck, SCHCAckReq, SCHCReceiverAbort, All1SCHCFragment, RegularSCHCFragment
from schc_protocols import LoRaWAN


def parse(message):
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

    Raises
    ------
    ValueError:
        Rule ID not defined in protocol
    RuntimeError:
        LoRaWAN cannot support fragmentation of message
    """
    rule_id = int.from_bytes(message[0:LoRaWAN().FPORT_LENGTH // 8], "big")
    if rule_id == LoRaWAN.ACK_ON_ERROR:
        return __parse_ack_on_error__(message)
    elif rule_id == LoRaWAN.ACK_ALWAYS:
        return __parse_ack_always__(message)
    elif rule_id == LoRaWAN.NOT_POSSIBLE:
        raise RuntimeError("Cannot fragment message under LoRaWAN protocol")
    else:
        raise ValueError("Rule ID not defined in protocol")


def __parse_ack_on_error__(message):
    """
    Parses message on ack_on_error mode

    Parameters
    ----------
    message : bytes
        Content received

    Returns
    -------
    SCHCMessage :
        SCHCMessage with attributes given by content received

    Raises
    ------
    AssertionError :
        Message receive do not match L2 Word size
    ValueError :
        Message of unknown type for LoRaWAN SCHC Compression
    """
    protocol = LoRaWAN(rule_id=LoRaWAN.ACK_ON_ERROR)
    bits_received = SCHCMessage.bytes_2_bits(message)
    length = len(bits_received)
    assert length % protocol.L2_WORD == 0, "Bits received does not match L2 word"
    pointer = protocol.RULE_SIZE + protocol.T + protocol.M
    bit_to_check = bits_received[pointer:pointer + 1]
    bits_to_check = bits_received[pointer:pointer + protocol.N]
    if length == protocol.L2_WORD * 2:
        if bits_to_check == "0" * protocol.N:
            return SCHCAckReq.from_bytes(message, protocol=protocol.id)
        else:
            return SCHCAck.from_bytes(message, protocol=protocol.id)
    elif length == protocol.L2_WORD * 3:
        if bit_to_check == "0":
            return SCHCAck.from_bytes(message, protocol=protocol.id)
        elif bit_to_check == "1":
            return SCHCReceiverAbort.from_bytes(message, protocol=protocol.id)
    elif length > protocol.L2_WORD * 3:
        if bits_to_check == "1" * protocol.N:
            return All1SCHCFragment.from_bytes(message, protocol=protocol.id)
        elif length >= protocol.L2_WORD * 2 + protocol.TILE_SIZE:
            return RegularSCHCFragment.from_bytes(message, protocol=protocol.id)
        else:
            return SCHCAck.from_bytes(message, protocol=protocol.id)
    else:
        raise ValueError("Message of unknown type for LoRaWAN SCHC Compression")


def __parse_ack_always__(message):
    """
    Parses message on ack_always mode

    Parameters
    ----------
    message : bytes
        Content received

    Returns
    -------
    SCHCMessage :
        SCHCMessage with attributes given by content received
    """
    protocol = LoRaWAN(rule_id=LoRaWAN.ACK_ALWAYS)
    bits_received = SCHCMessage.bytes_2_bits(message)
    length = len(bits_received)
    assert length % protocol.L2_WORD == 0, "Bits received does not match L2 word"
    pointer = protocol.RULE_SIZE + protocol.T + protocol.M
    bit_to_check = bits_received[pointer:pointer + 1]
    if length == protocol.L2_WORD * 2:
        return SCHCAck.from_bytes(message, protocol=protocol.id)
    elif length == protocol.L2_WORD * 3:
        if bit_to_check == "0":
            return RegularSCHCFragment.from_bytes(message, protocol=protocol.id)
        elif bit_to_check == "1":
            return SCHCReceiverAbort.from_bytes(message, protocol=protocol.id)
    elif length > protocol.L2_WORD * 3:
        if bit_to_check == "0":
            return RegularSCHCFragment.from_bytes(message, protocol=protocol.id)
        elif bit_to_check == "1":
            return All1SCHCFragment.from_bytes(message, protocol=protocol.id)
    else:
        raise ValueError("Message of unknown type for LoRaWAN SCHC Compression")
