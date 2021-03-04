""" schc_sender: SCHC Finite State Machine Sender Behaviour """

from __future__ import annotations
from abc import ABC, abstractmethod
from schc_base import SCHCTimer, SCHCObject
from schc_messages import SCHCAck, SCHCReceiverAbort, SCHCMessage
from schc_modes import SCHCFiniteStateMachine
from schc_parsers import SCHCParser
from schc_protocols import SCHCProtocol


class SCHCSender(SCHCFiniteStateMachine, ABC):
    """
    SCHC Finite State Machine for Receiver behaviour

    Attributes
    ----------
    protocol
    state
    retransmission_timer : Timer
        Retransmission Timer to abort retransmitting SCHC Messages
    packet : bytes
        Packet to send
    residue : str
        Compression residue (as bits)
    remaining_packet : str
        Rest of packet to send encoding as 0 and 1 string
    init_state : SCHCSender.InitialPhase
        Initial Phase of State Machine
    sending_state : SCHCSender.SendingPhase
        Sending Phase of State Machine
    waiting_state : SCHCSender.WaitingPhase(self)
        Waiting Phase of State Machine
    """
    class SenderState(SCHCFiniteStateMachine.State, ABC):
        """
        Sender State

        Attributes
        ----------
        state_machine : SCHCSender
            SCHC Receiver State Machine associated
        """
        def __init__(self, state_machine: SCHCSender) -> None:
            super().__init__(state_machine)
            self.__type__ = "Sender"
            return

        @abstractmethod
        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Generates a SCHC message to send

            Parameters
            ----------
            mtu : int
                Size of MTU available (in bytes)

            Returns
            -------
            SCHCMessage:
                SCHC Message to send

            Raises
            ------
            RuntimeError
                No more SCHC Message to send on current state
            """
            pass

        def receive_message(self, message: bytes) -> SCHCMessage:
            """
            Does something when receiving bytes

            Parameters
            ----------
            message : bytes
                A message as bytes

            Returns
            -------
            SCHCMessage:
                SCHC Message to send

            Raises
            ------
            ValueError
                In case bytes received could not be decoded to a SCHC Message
            """
            schc_message = SCHCParser.from_bytes(self.state_machine.protocol, message)
            if isinstance(schc_message, SCHCAck):
                return self.receive_schc_ack(schc_message)
            elif isinstance(schc_message, SCHCReceiverAbort):
                return self.receive_schc_receiver_abort(schc_message)
            else:
                pass

        @abstractmethod
        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCAck
                Message received

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            pass

        @abstractmethod
        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCReceiverAbort
                Message received

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            pass

    class InitialPhase(SenderState, ABC):
        """
        Initial phase: Initialization of Sender
        """
        def __init__(self, state_machine: SCHCSender) -> None:
            super().__init__(state_machine)
            self.__name__ = "Initial Phase"
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            pass

    class SendingPhase(SenderState, ABC):
        """
        Sending phase: Sending SCHC Message and receiving SCHC Ack
        """
        def __init__(self, state_machine: SCHCSender) -> None:
            super().__init__(state_machine)
            self.__name__ = "Sending Phase"
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            pass

    class WaitingPhase(SenderState, ABC):
        """
        Waiting phase: Waiting SCHC Ack and not active sending SCHC Messages
        """
        def __init__(self, state_machine: SCHCSender) -> None:
            super().__init__(state_machine)
            self.__name__ = "Waiting Phase"
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int, payload: bytes, residue: str = "", dtag: int = None) -> None:
        """
        Constructor

        Parameters
        ----------
        protocol
        rule_id
        payload : bytes
            Payload to fragment
        residue : str
            Bits (as a string) obtained as residue of compression process
        dtag
        """
        super().__init__(protocol, rule_id, dtag=dtag)
        self.retransmission_timer = SCHCTimer(self.on_expiration_time, protocol.RETRANSMISSION_TIMER)
        self.retransmission_timer.stop()
        self.packet = payload
        self.residue = residue
        self.remaining_packet = residue + SCHCObject.bytes_2_bits(payload)
        self.rcs = self.protocol.calculate_rcs(self.remaining_packet)
        self.init_state = SCHCSender.InitialPhase(self)
        self.sending_state = SCHCSender.SendingPhase(self)
        self.waiting_state = SCHCSender.WaitingPhase(self)
        self.state = self.init_state
        return

    def generate_message(self, mtu: int) -> SCHCMessage:
        """
        Generates a SCHC message to send

        Parameters
        ----------
        mtu : int
            Size of MTU available (in bytes)

        Returns
        -------
        List[SCHCMessage] :
            List of SCHC Messages to send

        Raises
        ------
        RuntimeError
            No more SCHC Message to send on current state
        """
        return self.state.generate_message(mtu)
