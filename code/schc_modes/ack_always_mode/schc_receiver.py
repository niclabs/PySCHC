""" schc_receiver: Ack-Always Mode Receiver Finite State Machine """

from typing import List
from schc_messages import SCHCSenderAbort, SCHCAckReq, All1SCHCFragment, RegularSCHCFragment, SCHCMessage
from schc_modes import SCHCReceiver
from schc_protocols import SCHCProtocol


class AckAlwaysModeSCHCReceiver(SCHCReceiver):
    """
    SCHC Receiver Finite State Machine for Ack-Always Mode

    Attributes
    ----------
    protocol
    state
    receiving_phase
    waiting_phase
    waiting_end_phase
    """
    class AcceptancePhase(SCHCReceiver.ReceivingPhase):
        """
        Acceptance Phase of receiver
        """
        def receive_message(self, message: bytes) -> SCHCMessage:
            pass

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> SCHCMessage:
            pass

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> SCHCMessage:
            pass

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> SCHCMessage:
            pass

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> SCHCMessage:
            pass

    class RetransmissionPhase(SCHCReceiver.WaitingPhase):
        """
        Retransmission Phase of receiver
        """
        def receive_message(self, message: bytes) -> SCHCMessage:
            pass

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> SCHCMessage:
            pass

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> SCHCMessage:
            pass

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> SCHCMessage:
            pass

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> SCHCMessage:
            pass

    class CleanUpPhase(SCHCReceiver.WaitingEndPhase):
        """
        Clean Up Phase of receiver
        """

        def receive_message(self, message: bytes) -> SCHCMessage:
            pass

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> SCHCMessage:
            pass

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> SCHCMessage:
            pass

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> SCHCMessage:
            pass

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> SCHCMessage:
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int) -> None:
        super().__init__(protocol, rule_id)
        self.receiving_phase = AckAlwaysModeSCHCReceiver.AcceptancePhase(self)
        self.waiting_phase = AckAlwaysModeSCHCReceiver.RetransmissionPhase(self)
        self.waiting_end_phase = AckAlwaysModeSCHCReceiver.CleanUpPhase(self)
        self.state = self.receiving_phase
        return
