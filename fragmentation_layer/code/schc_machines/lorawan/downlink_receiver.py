""" downlink_receiver: Downlink receiver state machine """

from __future__ import annotations
from typing import List
from schc_machines import SCHCReceiver, AckAlways
from schc_messages import SCHCMessage, RegularSCHCFragment, SCHCAck, All1SCHCFragment
from schc_protocols import SCHCProtocol


class DownlinkReceiver(AckAlways, SCHCReceiver):
    """
    Downlink Receiver State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    """
    class TemplatePhase(SCHCReceiver.ReceiverState):
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

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> None:
            """
            Actions when receive a Regular SCHC Fragment

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> None:
            """
            Actions when receive a All-1 SCHC Fragment

            Parameters
            ----------
            schc_message : All1SCHCFragment
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> None:
            """
            Actions when receive a SCHC Ack Request

            Parameters
            ----------
            schc_message : SCHCAckReq
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> None:
            """
            Actions when receive a SCHC Sender Abort

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

    def __init__(self, protocol: SCHCProtocol, dtag: int = None) -> None:
        super().__init__(protocol, dtag=dtag)
        AckAlways.__init__(self)
        self.states["name_your_state"] = DowblinkReceiver.TemplatePhase(self)
        # self.states["other_state"] = DownlinkReceiver.OtherPhase(self)
        self.state = self.states["name_your_phase"]  # Initial State
        self.state.enter_state()  # This generates logs to know current states
        # Check schc_machines/schc_receiver.py and schc_machines/schc_fsm.py
        # to check other attributes of this class.
        # Anything else needed
        return
