""" schc_receiver: SCHC Finite State Machine Receiver Behaviour """

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from schc_base import Timer, Bitmap
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
    bitmap : Bitmap
        Bitmap to register tile received
    inactivity_timer : Timer
        Inactivity Timer to abort waiting for SCHC Message
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
        def receive_message(self, message: bytes) -> List[SCHCMessage]:
            """
            Receives a message and does something

            Parameters
            ----------
            message : bytes
                Received Message

            Returns
            -------
            List[SCHCMessage] :
                List of SCHC Messages to send
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
                return list()

        @abstractmethod
        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> List[SCHCMessage]:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                Message received

            Returns
            -------
            List[SCHCMessage] :
                List of SCHC Messages to send
            """
            return list()

        @abstractmethod
        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> List[SCHCMessage]:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : All1SCHCFragment
                Message received

            Returns
            -------
            List[SCHCMessage] :
                List of SCHC Messages to send
            """
            return list()

        @abstractmethod
        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> List[SCHCMessage]:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCAckReq
                Message received

            Returns
            -------
            List[SCHCMessage] :
                List of SCHC Messages to send
            """
            return list()

        @abstractmethod
        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> List[SCHCMessage]:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                Message received

            Returns
            -------
            List[SCHCMessage] :
                List of SCHC Messages to send
            """
            return list()

    def __init__(self, protocol: SCHCProtocol, rule_id: int, dtag: int = -1) -> None:
        super().__init__(protocol, rule_id, dtag=dtag)
        self.bitmap = Bitmap(protocol)
        self.inactivity_timer = Timer(protocol.INACTIVITY_TIMER)
        return
