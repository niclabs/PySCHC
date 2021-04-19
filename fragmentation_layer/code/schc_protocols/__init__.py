""" schc_protocols: Package of Protocol implementation """

from schc_protocols.schc_protocol import SCHCProtocol
from schc_protocols.lorawan import LoRaWAN
from schc_protocols.sigfox import Sigfox


def get_protocol(protocol, rule_id=0):
    """
    Generates protocol from id defined

    Parameters
    ----------
    protocol : int
        A valid Number
    rule_id : int
        Rule ID given

    Returns
    -------
    SCHCProtocol :
        SCHC Protocol associated to number given

    Raises
    ------
    NotImplementedError
        Any Protocol currently not implemented
    """
    if protocol == SCHCProtocol.LoRaWAN:
        return LoRaWAN(rule_id=rule_id)
    else:
        raise NotImplementedError("Protocol not implemented.\n"
                                  "Available Protocols:\n"
                                  "\t1:\tLoRaWAN")
