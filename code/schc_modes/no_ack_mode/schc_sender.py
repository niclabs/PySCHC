""" schc_sender: No-Ack Mode Sender Finite State Machine """
from schc_messages import SCHCReceiverAbort, SCHCAck
from schc_modes import SCHCSender


class NoAckModeSCHCSender(SCHCSender):
    """
    SCHC Sender Finite State Machine for No-Ack Mode
    """
    def receive_schc_ack(self, schc_message: SCHCAck) -> List[SCHCMessage]:
        pass

    def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> List[SCHCMessage]:
        pass
