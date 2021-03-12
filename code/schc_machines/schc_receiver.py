""" schc_receiver: SCHC Finite State Machine Receiver Behaviour """

from __future__ import annotations
from abc import ABC
from schc_base import SCHCTimer
from schc_messages import RegularSCHCFragment, All1SCHCFragment, SCHCAckReq, SCHCSenderAbort, SCHCMessage, SCHCPayload
from schc_machines import SCHCFiniteStateMachine
from schc_parsers import SCHCParser
from schc_protocols import SCHCProtocol


class SCHCReceiver(SCHCFiniteStateMachine, ABC):
    """
    SCHC Finite State Machine for Receiver behaviour

    Attributes
    ----------
    protocol
    payload : SCHCPayload
        Payload reassembled
    inactivity_timer : Timer
        Inactivity Timer to abort waiting for SCHC Message
    """
    __type__ = "Receiver"

    class ReceiverState(SCHCFiniteStateMachine.State, ABC):
        """
        Receiver State
        """
        def receive_message(self, message: bytes) -> None:
            """
            Receives a message and does something

            Parameters
            ----------
            message : bytes
                Received Message

            Returns
            -------
            None, alter state
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
                raise RuntimeError("Bytes received could not be decoded")

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> None:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                Message received

            Returns
            -------
            None:
                Alter state

            Raises
            ------
            RuntimeError
                Behaviour unreachable
            """
            raise RuntimeError("Behaviour unreachable")

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> None:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : All1SCHCFragment
                Message received

            Returns
            -------
            None, alter state

            Raises
            ------
            RuntimeError
                Behaviour unreachable
            """
            raise RuntimeError("Behaviour unreachable")

        def receive_schc_ack_req(self, schc_message: SCHCAckReq) -> None:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCAckReq
                Message received

            Returns
            -------
            None, alter state

            Raises
            ------
            RuntimeError
                Behaviour unreachable
            """
            raise RuntimeError("Behaviour unreachable")

        def receive_schc_sender_abort(self, schc_message: SCHCSenderAbort) -> None:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                Message received

            Returns
            -------
            None, alter state

            Raises
            ------
            RuntimeError
                Behaviour unreachable
            """
            raise RuntimeError("Behaviour unreachable")

    def __init__(self, protocol: SCHCProtocol, dtag: int = None) -> None:
        super().__init__(protocol, dtag=dtag)
        self.payload: SCHCPayload = SCHCPayload()
        self.inactivity_timer = SCHCTimer(self.on_expiration_time, protocol.INACTIVITY_TIMER)
        return
