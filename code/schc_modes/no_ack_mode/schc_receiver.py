""" schc_receiver: No-Ack Mode Receiver Finite State Machine """

from schc_messages import SCHCSenderAbort, SCHCAckReq, All1SCHCFragment, RegularSCHCFragment
from schc_modes import SCHCReceiver


class NoAckModeSCHCReceiver(SCHCReceiver):
    """
    SCHC Receiver Finite State Machine for No-Ack Mode
    """
    def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> List[SCHCMessage]:
        pass

    def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> List[SCHCMessage]:
        pass

    def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> List[SCHCMessage]:
        pass

    def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> List[SCHCMessage]:
        pass
