""" schc_receiver: SCHC Finite State Machine Receiver Behaviour """

from __future__ import annotations
from abc import ABC, abstractmethod
from schc_base import SCHCTimer, Bitmap
from schc_messages import RegularSCHCFragment, All1SCHCFragment, SCHCAckReq, SCHCSenderAbort, SCHCMessage
from schc_modes import SCHCFiniteStateMachine
from schc_parsers import SCHCParser
from schc_protocols import SCHCProtocol


class SCHCReceiver(SCHCFiniteStateMachine, ABC):
    """
    SCHC Finite State Machine for Receiver behaviour

    Attributes
    ----------
    protocol
    state
    bitmap : Bitmap
        Bitmap to register tile received
    inactivity_timer : Timer
        Inactivity Timer to abort waiting for SCHC Message
    receiving_phase : SCHCReceiver.ReceivingPhase
        Receiving phase of State Machine
    waiting_phase : SCHCReceiver.WaitingPhase
        Waiting phase of State Machine
    waiting_end_phase : SCHCReceiver.WaitingEndPhase
        Waiting End phase of State Machine
    """
    class ReceiverState(SCHCFiniteStateMachine.State, ABC):
        """
        Receiver State

        Attributes
        ----------
        state_machine : SCHCReceiver
            SCHC Receiver State Machine associated
        """
        def __init__(self, state_machine: SCHCReceiver) -> None:
            super().__init__(state_machine)

        @abstractmethod
        def receive_message(self, message: bytes) -> SCHCMessage:
            """
            Receives a message and does something

            Parameters
            ----------
            message : bytes
                Received Message

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            schc_message = SCHCParser.from_bytes(self.state_machine.protocol, message)
            if isinstance(schc_message, RegularSCHCFragment):
                return self.receive_regular_schc_fragment(schc_message)
            elif isinstance(schc_message, All1SCHCFragment):
                return self.receive_all1_schc_fragment(schc_message)
            elif isinstance(schc_message, SCHCAckReq):
                return self.receive_schc_ack_req(schc_message)
            elif isinstance(schc_message, SCHCSenderAbort):
                return self.receive_schc_sender_abort(schc_message)
            else:
                pass

        @abstractmethod
        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> SCHCMessage:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                Message received

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            pass

        @abstractmethod
        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> SCHCMessage:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : All1SCHCFragment
                Message received

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            pass

        @abstractmethod
        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> SCHCMessage:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCAckReq
                Message received

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            pass

        @abstractmethod
        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> SCHCMessage:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                Message received

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            pass

    class ReceivingPhase(ReceiverState, ABC):
        """
        Receiving phase: Receiver receiving tiles
        """
        def __init__(self, state_machine: SCHCReceiver) -> None:
            super().__init__(state_machine)
            return

    class WaitingPhase(ReceiverState, ABC):
        """
        Waiting phase: Receiver waiting for transmission of next window
        """
        def __init__(self, state_machine: SCHCReceiver) -> None:
            super().__init__(state_machine)
            return

    class WaitingEndPhase(ReceiverState, ABC):
        """
        Waiting end phase: Waiting for All-1 Fragment Message
        """
        def __init__(self, state_machine: SCHCReceiver) -> None:
            super().__init__(state_machine)
            return

    def __init__(self, protocol: SCHCProtocol, rule_id: int, dtag: int = None) -> None:
        super().__init__(protocol, rule_id, dtag=dtag)
        self.bitmap = Bitmap(protocol)
        self.inactivity_timer = SCHCTimer(self.on_expiration_time, protocol.INACTIVITY_TIMER)
        self.receiving_phase = SCHCReceiver.ReceivingPhase(self)
        self.waiting_phase = SCHCReceiver.WaitingPhase(self)
        self.waiting_end_phase = SCHCReceiver.WaitingEndPhase(self)
        self.state = self.receiving_phase
        return
