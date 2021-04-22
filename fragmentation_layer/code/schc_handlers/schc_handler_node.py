""" schc_handler_node: SCHC Handler Node Class """

from schc_handlers import SCHCHandler
from schc_protocols import LoRaWAN, SCHCProtocol, get_protocol


class SCHCHandlerGateway(SCHCHandler):

    def __init__(self, protocol):
        super().__init__(protocol)

    def send_package(self, rule_id, packet, dtag=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            if rule_id == LoRaWAN.ACK_ON_ERROR:
                from schc_machines.lorawan import AckOnErrorSender
                self.assign_session(rule_id, dtag, AckOnErrorSender(LoRaWAN(LoRaWAN.ACK_ON_ERROR), packet))
            else:
                raise ValueError("Rule ID not allowed for sending a message from a gateway")
        else:
            raise NotImplementedError("Just LoRaWAN implemented")
        self.__sessions__[rule_id][dtag].receive_message(message)

    def receive(self, rule_id, dtag, message, f_port=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            if rule_id == LoRaWAN.ACK_ALWAYS:
                # message received
                from schc_machines.lorawan import AckAlwaysReceiver
                self.assign_session(rule_id, dtag, AckAlwaysReceiver(LoRaWAN(LoRaWAN.ACK_ON_ERROR)))
                self.__sessions__[rule_id][dtag].receive_message(message)
            elif rule_id == LoRaWAN.ACK_ON_ERROR:
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
