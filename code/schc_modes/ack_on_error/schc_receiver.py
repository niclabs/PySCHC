""" schc_receiver: SCHC Ack-on-Error Mode Receiver Finite State Machine """

from schc_modes import SCHCReceiver
from schc_protocols import SCHCProtocol


class AckOnErrorSCHCReceiver(SCHCReceiver):
    """
    SCHC Finite State Machine for Ack On Error Sender behaviour

    Attributes
    ----------
    protocol
    state
    receiving_phase
    waiting_phase
    waiting_end_phase
    """
    class ReceivingPhase(SCHCReceiver.ReceivingPhase):
        """
        Receiving Phase of Ack on Error
        """

    class WaitingPhase(SCHCReceiver.WaitingPhase):
        """
        Waiting Phase of Ack on Error
        """

    class WaitingEndPhase(SCHCReceiver.WaitingEndPhase):
        """
        Waiting End Phase of Ack on Error
        """

    def __init__(self, protocol: SCHCProtocol, rule_id: int, dtag: int = None) -> None:
        super().__init__(protocol, rule_id, dtag=dtag)
        self.receiving_phase = AckOnErrorSCHCReceiver.ReceivingPhase(self)
        self.waiting_phase = AckOnErrorSCHCReceiver.WaitingPhase(self)
        self.waiting_end_phase = AckOnErrorSCHCReceiver.WaitingEndPhase(self)
        self.state = self.receiving_phase
        return
