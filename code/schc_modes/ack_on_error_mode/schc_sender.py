""" schc_sender: Ack-on-Error Mode Sender Finite State Machine """

from schc_messages import SCHCReceiverAbort, SCHCAck
from schc_modes import SCHCSender
from schc_protocols import SCHCProtocol


class AckOnErrorModeSCHCSender(SCHCSender):
    """
    SCHC Sender Finite State Machine for Ack-on-Error Mode
    """
    class TransmissionPhase(SCHCSender.SenderState):
        """
        Transmission Phase for sender
        """
        def receive_message(self, message: bytes) -> List[SCHCMessage]:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> List[SCHCMessage]:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> List[SCHCMessage]:
            pass

    class RetransmissionPhase(SCHCSender.SenderState):
        """
        Retransmission Phase for sender
        """
        def receive_message(self, message: bytes) -> List[SCHCMessage]:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> List[SCHCMessage]:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> List[SCHCMessage]:
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int) -> None:
        super().__init__(protocol, rule_id)
        self.transmission_phase = AckOnErrorModeSCHCSender.TransmissionPhase(self)
        self.retransmission_phase = AckOnErrorModeSCHCSender.RetransmissionPhase(self)
        self.state = self.transmission_phase
        return
