""" schc_fragmenter_gateway: SCHC Fragmenter Gateway Class """

from schc_base import SCHCObject
from schc_protocols import LoRaWAN, SCHCProtocol, get_protocol


class SCHCHandlerGateway:

    def __init__(self, protocol):
        self.__protocol__ = get_protocol(protocol)
        self.__sessions__ = dict()

    def identify_session_from_message(self, message, f_port=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            rule_id = int.from_bytes(f_port, "big")
        else:
            raise NotImplementedError("Just LoRaWAN implemented")
        protocol = get_protocol(self.__protocol__.id)
        protocol.set_rule_id(rule_id)
        dtag = SCHCObject.bytes_2_bits(message)[:protocol.T]
        if len(dtag) == 0:
            dtag = None
        else:
            dtag = int(dtag, 2)
        return (rule_id, dtag)

    def send_package(self, rule_id, packet, dtag=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            if rule_id == LoRaWAN.ACK_ALWAYS:
                from schc_machines.lorawan import AckAlwaysSender
                self.assign_session(rule_id, dtag, AckAlwaysSender(LoRaWAN(LoRaWAN.ACK_ON_ERROR), packet))
            else:
                raise ValueError("Rule ID not allowed for sending a message from a gateway")
        else:
            raise NotImplementedError("Just LoRaWAN implemented")
        self.__sessions__[rule_id][dtag].receive_message(message)

    def receive(self, rule_id, dtag, message, f_port=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            if rule_id == LoRaWAN.ACK_ON_ERROR:
                # message received
                from schc_machines.lorawan import AckOnErrorReceiver
                self.assign_session(rule_id, dtag, AckOnErrorReceiver(LoRaWAN(LoRaWAN.ACK_ON_ERROR)))
                self.__sessions__[rule_id][dtag].receive_message(message)
            elif rule_id == LoRaWAN.ACK_ALWAYS:
                # response received
                self.__sessions__[rule_id][dtag].receive_message(message)
            else:
                pass
                # TODO compression
        else:
            raise NotImplementedError("Just LoRaWAN implemented")

    def generate_message(self, rule_id, dtag, mtu=512):
        try:
            return self.__sessions__[rule_id][dtag].generate_message(mtu).as_bytes()
        except GeneratorExit:
            return b''

    def assign_session(self, rule_id, dtag, machine):
        if rule_id not in self.__sessions__.keys():
            self.__sessions__[rule_id] = dict()
        if dtag not in self.__sessions__[rule_id].keys():
            self.__sessions__[rule_id][dtag] = machine
