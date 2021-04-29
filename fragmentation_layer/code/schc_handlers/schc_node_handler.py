""" schc_handler_node: SCHC Handler Node Class """

from schc_handlers import SCHCHandler
from schc_protocols import LoRaWAN, SCHCProtocol


class SCHCNodeHandler(SCHCHandler):

    def __init__(self, protocol, mtu):
        super().__init__(protocol, mtu)

    def send_package(self, packet):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            from schc_machines.lorawan import AckOnErrorSender
            self.assign_session(LoRaWAN.ACK_ON_ERROR, None, AckOnErrorSender(LoRaWAN(LoRaWAN.ACK_ON_ERROR), packet))
        else:
            raise NotImplementedError("Just LoRaWAN implemented")

    def receive(self, rule_id, dtag, message, f_port=None):
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            if rule_id == LoRaWAN.ACK_ALWAYS:
                # message received
                from schc_machines.lorawan import AckAlwaysReceiver
                self.assign_session(rule_id, dtag, AckAlwaysReceiver(LoRaWAN(LoRaWAN.ACK_ALWAYS)))
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

    def start(self, s):
        while True:
            for rule_id in self.__sessions__.keys():
                for dtag in self.__sessions__[rule_id].keys():
                    machine = self.__sessions__[rule_id][dtag]
                    message = machine.generate_message(self.__mtu__)

                    if message is not None:
                        s.setblocking(True)
                        print(message.as_text())

                        # send some data
                        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
                            s.bind(int(message.as_bytes()[0]))
                            s.send(message.as_bytes()[1:])
                        else:
                            s.send(message.as_bytes())

                        # make the socket non-blocking
                        # (because if there's no data received it will block forever...)
                        s.setblocking(False)

                        # get any data received (if any...)
                        data = s.recvfrom(512)
                        print(data)
                        if data[0] != b'':
                            r, d = self.identify_session_from_message(data)
                            self.receive(r, d, data)
