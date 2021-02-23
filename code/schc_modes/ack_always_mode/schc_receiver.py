""" schc_receiver: Ack-Always Mode Receiver Finite State Machine """

from typing import List
from schc_messages import SCHCSenderAbort, SCHCAckReq, All1SCHCFragment, RegularSCHCFragment, SCHCMessage
from schc_modes import SCHCReceiver
from schc_protocols import SCHCProtocol


class AckAlwaysModeSCHCReceiver(SCHCReceiver):
    """
    SCHC Receiver Finite State Machine for Ack-Always Mode
    """
    class AcceptancePhase(SCHCReceiver.ReceiverState):
        """
        Acceptance Phase of receiver
        """
        def receive_message(self, message: bytes) -> List[SCHCMessage]:
            pass

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> List[SCHCMessage]:
            pass

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> List[SCHCMessage]:
            pass

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> List[SCHCMessage]:
            pass

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> List[SCHCMessage]:
            pass

    class RetransmissionPhase(SCHCReceiver.ReceiverState):
        """
        Retransmission Phase of receiver
        """
        def receive_message(self, message: bytes) -> List[SCHCMessage]:
            pass

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> List[SCHCMessage]:
            pass

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> List[SCHCMessage]:
            pass

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> List[SCHCMessage]:
            pass

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> List[SCHCMessage]:
            pass

    class CleanUpPhase(SCHCReceiver.ReceiverState):
        """
        Clean Up Phase of receiver
        """

        def receive_message(self, message: bytes) -> List[SCHCMessage]:
            pass

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> List[SCHCMessage]:
            pass

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> List[SCHCMessage]:
            pass

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> List[SCHCMessage]:
            pass

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> List[SCHCMessage]:
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int) -> None:
        super().__init__(protocol, rule_id)
        self.acceptance_phase = AckAlwaysModeSCHCReceiver.AcceptancePhase(self)
        self.retransmission_phase = AckAlwaysModeSCHCReceiver.RetransmissionPhase(self)
        self.clean_up_phase = AckAlwaysModeSCHCReceiver.CleanUpPhase(self)
        self.state = self.acceptance_phase
        return
