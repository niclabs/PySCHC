""" schc_gateway_handler: SCHC Gateway Handler Class """
import sys

if sys.implementation.name != 'micropython':
    import requests
    import base64

from schc_handlers import SCHCHandler
from schc_protocols import LoRaWAN, SCHCProtocol


class SCHCGatewayHandler(SCHCHandler):

    def __init__(self, protocol, mtu):
        super().__init__(protocol, mtu)

    def send_package(self, packet):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            from schc_machines.lorawan import AckAlwaysSender
            self.assign_session(LoRaWAN.ACK_ALWAYS, None, AckAlwaysSender(LoRaWAN(LoRaWAN.ACK_ALWAYS), packet))
        else:
            raise NotImplementedError("Just LoRaWAN implemented")

    def receive(self, rule_id, dtag, message):
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

    def handle(self, message, f_port=None, url=None, dev_id=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            r,d = self.identify_session_from_message(message, bytes([f_port]))
            self.receive(r,d,bytes([f_port]) + message)
            response = self.generate_message(r,d)
        else:
            raise NotImplementedError("Just LoRaWAN implemented")
        if url is None:
            return response
        else:
            post_obj = {
                "dev_id": dev_id,
                "port": f_port,
                "confirmed": False,
                "payload_raw": base64.b64encode(response).decode("utf-8")
            }
            requests.post(url, post_obj)

    def generate_message(self, rule_id, dtag, mtu=512):
        message = self.__sessions__[rule_id][dtag].generate_message(mtu)
        if message is None:
            return message
        else:
            return message.as_bytes()
