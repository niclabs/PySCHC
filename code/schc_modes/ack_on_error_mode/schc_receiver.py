""" schc_receiver: Ack-on-Error Mode Receiver Finite State Machine """

from schc_messages import SCHCSenderAbort, SCHCAckReq, All1SCHCFragment, RegularSCHCFragment
from schc_modes import SCHCReceiver
from schc_protocols import SCHCProtocol


class AckOnErrorSCHCReceiver(SCHCReceiver):
    """
    SCHC Receiver Finite State Machine for Ack-on-Error Mode
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

    def __init__(self, protocol: SCHCProtocol, rule_id: int) -> None:
        super().__init__(protocol, rule_id)
        self.acceptance_phase = AckOnErrorSCHCReceiver.AcceptancePhase(self)
        self.state = self.acceptance_phase
        return
