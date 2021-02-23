""" schc_fsm: SCHC Finite State Machine Abstract Class """

from __future__ import annotations
from abc import ABC
from typing import List
from warnings import warn
from schc_base import AttemptsCounter
from schc_messages import SCHCMessage
from schc_protocols import SCHCProtocol


class SCHCFiniteStateMachine(ABC):
    """
    Finite State Machine of Sender/Receiver (Fragmenter/Ensembler)
    behaviours

    Attributes
    ----------
    protocol : SCHCProtocol
        Protocol to use
    __rule_id__ : int
        Rule ID to determines behaviour, it cannot (supposedly) change
    __dtag__ : int
        DTag to determines behaviour, it cannot (supposedly) change.
        -1 Implies Dtag is not used and there is just one Packet for Rule ID
    __current_window__ : int
        Current window being processed
    attempts : AttemptsCounter
        Attempts Counter that register request for SCHC ACKs
    state : State
        Current State of State Machine
    rcs : str
        Calculated rcs
    """
    class State:
        """
        Define the current state of a SCHC Finite State Machine

        Attributes
        ----------
        state_machine : SCHCFiniteStateMachine
            State Machine associated
        """
        def __init__(self, state_machine: SCHCFiniteStateMachine) -> None:
            self.state_machine = state_machine
            return

        def receive_message(self, message: bytes) -> SCHCMessage:
            """
            Does something when receiving bytes

            Parameters
            ----------
            message : bytes
                A message as bytes

            Returns
            -------
            SCHCMessage :
                List of SCHC Messages to send
            """
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int, dtag: int = -1) -> None:
        """
        Constructor

        Parameters
        ----------
        protocol : SCHCProtocol
            Protocol to use
        rule_id : int
            Rule ID to identify behaviour
        dtag : int, optional
            Dtag to identify behaviour, Default: -1 implying there is just
            one SCHC Packet for Rule ID at a time
        """
        self.protocol = protocol
        self.__rule_id__ = rule_id
        if protocol.RULE_ID != rule_id:
            warn("Protocol given has a different Rule ID, changing to match, Rule ID of finite state machine")
            protocol.set_rule_id(rule_id)
        if protocol.T == 0:
            self.__dtag__ = -1
        else:
            self.__dtag__ = dtag
        self.__current_window__ = 0
        self.attempts = AttemptsCounter(protocol.MAX_ACK_REQUEST)
        self.state = SCHCFiniteStateMachine.State(self)
        self.rcs = ""
        return

    def receive_message(self, message: bytes) -> SCHCMessage:
        """
        Does something when receiving bytes

        Parameters
        ----------
        message : bytes
            A message as bytes

        Returns
        -------
        SCHCMessage :
            SCHC Message to send as a response
        """
        return self.state.receive_message(message)
