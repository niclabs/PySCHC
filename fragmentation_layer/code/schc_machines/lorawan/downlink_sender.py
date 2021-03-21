""" downlink_sender: Downlink sender state machine """

from __future__ import annotations
from schc_machines import SCHCSender, AckAlways
from schc_messages import SCHCMessage, SCHCAck, SCHCReceiverAbort
from schc_protocols import SCHCProtocol


class DownlinkSender(AckAlways, SCHCSender):
    """
    Downlink Sender State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    residue
    """
    class TemplatePhase(SCHCSender.SenderState):
        """
        # TODO:
        This is a state. Change as needed and copy/paste to 
        implement other state
        """
        __name__ = "Name this phase"

        # You can delete any method that is not using on the state
        # Or implement any of the following:

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Generates SCHC Message when this method is
            called. Make sure size (access with method schc_message.size),
            in bits, is less than mtu, in bytes.
            """
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> None:
            """
            Actions when receive a SCHC Ack Message

            Parameters
            ----------
            schc_message : SCHCAck
                SCHCAck received

            Returns
            -------
            None, alter state
            """
            return

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> None:
            """
            Actions when receive a SCHC Receiver Abort Message

            Parameters
            ----------
            schc_message : SCHCReceiverAbort
                Message received

            Returns
            -------
            None, alter state
            """
            return

    def __init__(self, protocol: SCHCProtocol, payload: bytes,
                 residue: str = "", dtag: int = None) -> None:
        super().__init__(protocol, payload, residue=residue, dtag=dtag)
        AckAlways.__init__(self)
        self.states["name_your_phase"] = DownlinkSender.TemplatePhase(self)
        # self.states["other_state"] = DownlinkSender.OtherPhase(self)
        self.state = self.states["name_your_phase"]  # Initial State
        self.state.enter_state()  # This generates logs to know current states
        # Calculates rcs, this is implemented in protocol (schc_protocols/lorawan.py)
        self.rcs = self.protocol.calculate_rcs(self.remaining_packet + padding)
        # Check schc_machines/schc_sender.py and schc_machines/schc_fsm.py
        # to check other attributes of this class.
        # Anything else needed
        return
