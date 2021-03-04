""" schc_fsm: SCHC Finite State Machine Abstract Class """

from __future__ import annotations
from abc import ABC
import logging
from typing import Callable
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
        class Logger:
            """
            SCHC Logger to log SCHC Fragmentation
            """
            def __init__(self, state: SCHCFiniteStateMachine.State) -> None:
                self.__state__ = state
                return

            def __log__(self, mode: Callable) -> None:
                mode("SCHC Fragment on '{}' mode, {} on '{}' state".format(
                    self.__state__.state_machine.__mode__,
                    self.__state__.__type__,
                    self.__state__.__name__
                ))
                second_line = "Protocol: {}, Rule ID: {}".format(
                    self.__state__.state_machine.protocol.__name__,
                    self.__state__.state_machine.__rule_id__
                )
                if self.__state__.state_machine.__dtag__ is not None:
                    second_line += ", DTag: {}".format(
                        self.__state__.state_machine.__dtag__
                    )
                mode(second_line)
                return

            def enter_state(self) -> None:
                """
                Logs entering a new state

                Returns
                -------
                None
                """
                self.__log__(logging.debug)
                return

            def schc_message(self, message: SCHCMessage) -> None:
                """
                Logs a SCHC Message

                Parameters
                ----------
                message : SCHCMessage
                    Message to show on logging

                Returns
                -------
                None
                """
                self.enter_state()
                logging.debug("Message:\n{}".format(message.as_text()))
                return

            def error(self, message: str) -> None:
                """
                Logs an error

                Parameters
                ----------
                message : str
                    Message to show

                Returns
                -------
                None
                """
                self.__log__(logging.error)
                logging.error(message)
                return

            def warning(self, message: str) -> None:
                """
                Logs a warn

                Parameters
                ----------
                message : str
                    Message to show

                Returns
                -------
                None
                """
                self.__log__(logging.warning)
                logging.warning(message)
                return

            def debug(self, message: str) -> None:
                """
                Logs an debug

                Parameters
                ----------
                message : str
                    Message to show

                Returns
                -------
                None
                """
                self.__log__(logging.debug)
                logging.debug(message)
                return

            def info(self, message: str) -> None:
                """
                Logs an error

                Parameters
                ----------
                message : str
                    Message to show

                Returns
                -------
                None
                """
                self.__log__(logging.info)
                logging.info(message)
                return

        def __init__(self, state_machine: SCHCFiniteStateMachine) -> None:
            self.state_machine = state_machine
            self.__name__ = "State"
            self.__type__ = "None"
            self._logger_ = SCHCFiniteStateMachine.State.Logger(self)
            return

        def enter_state(self) -> None:
            """
            Logs enter on this state

            Returns
            -------
            None
            """
            self._logger_.enter_state()
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
            SCHCMessage:
                SCHC Message to send
            """
            pass

        def on_expiration_time(self) -> None:
            """
            Behaviour on time expiration

            Returns
            -------
            None
            """
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int, dtag: int = None) -> None:
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
            self.__dtag__ = None
        else:
            self.__dtag__ = dtag
        self.__current_window__ = 0
        self.attempts = AttemptsCounter(protocol.MAX_ACK_REQUEST)
        self.state = SCHCFiniteStateMachine.State(self)
        self.rcs = ""
        self.__mode__ = "None"
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
        SCHCMessage:
                SCHC Message to send
        """
        return self.state.receive_message(message)

    def on_expiration_time(self) -> None:
        """
        Behaviour on time expiration

        Returns
        -------
        None
        """
        self.state.on_expiration_time()
