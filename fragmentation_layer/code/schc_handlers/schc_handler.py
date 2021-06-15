""" schc_handler: SCHC Handler (Super) Class """

from schc_base import SCHCObject
from schc_protocols import SCHCProtocol, get_protocol
from schc_compression import SCHC_Compressor, SCHC_Decompressor, SCHC_RuleManager


# TODO: 
class SCHCHandler:

    def __init__(self, protocol, mtu):
        self.__protocol__ = get_protocol(protocol)
        self.__sessions__ = dict()
        self.__mtu__ = mtu
        rm = SCHC_RuleManager()
        # TODO: add rules
        self.__compressor__ = SCHC_Compressor(rm)
        self.__decompressor__ = SCHC_Decompressor(rm)

    def identify_session_from_message(self, message, f_port=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            rule_id = f_port
        else:
            raise NotImplementedError("Just LoRaWAN implemented")
        protocol = get_protocol(self.__protocol__.id)
        protocol.set_rule_id(rule_id)
        dtag = SCHCObject.bytes_2_bits(message)[:protocol.T]
        if len(dtag) == 0:
            dtag = None
        else:
            dtag = int(dtag, 2)
        return rule_id, dtag

    def send_package(self, packet):
        return

    def receive(self, rule_id, dtag, message):
        return

    def assign_session(self, rule_id, dtag, machine):
        if rule_id not in self.__sessions__.keys():
            self.__sessions__[rule_id] = dict()
        if dtag not in self.__sessions__[rule_id].keys():
            self.__sessions__[rule_id][dtag] = machine
