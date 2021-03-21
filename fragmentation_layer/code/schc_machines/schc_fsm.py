""" schc_fsm: SCHC Finite State Machine Abstract Class """

from __future__ import annotations
import logging
import sys
from abc import ABC
from typing import Callable, Dict, List
from machine import Timer
from schc_base import AttemptsCounter, Bitmap
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
    __last_window__ : bool
        Whether current window is the last window
    __fcn__ : int
        Current fcn in progress of window
    bitmap : Bitmap
        Bitmap of current window
    attempts : AttemptsCounter
        Attempts Counter that register request for SCHC ACKs
    state : State
        Current State of State Machine
    rcs : str
        Calculated rcs
    __exit_msg__ : str
        Message to raise when error state
    __end_msg__ : str
        Message to raise when end state
    message_to_send : List[SCHCMessage]
        Queued message to be send prior next state
    """
    __mode__ = "None"
    __type__ = "None"

    class State:
        """
        Define the current state of a SCHC Finite State Machine

        Attributes
        ----------
        state_machine : SCHCFiniteStateMachine
            State Machine associated
        """
        __name__ = "State"

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
                    self.__state__.state_machine.__type__,
                    self.__state__.__name__
                ))
                second_line = "\tProtocol: {}, Rule ID: {}".format(
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
                logging.debug("\tMessage:\n{}".format(message.as_text()))
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
                logging.error("\t{}".format(message))
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
                logging.warning("\t{}".format(message))
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
                logging.debug("\t{}".format(message))
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
                logging.info("\t{}".format(message))
                return

        def __init__(self, state_machine: SCHCFiniteStateMachine) -> None:
            self.state_machine = state_machine
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
            GeneratorExit
                No more SCHC Message to send on current state
            """
            raise GeneratorExit("No more message to send")

        def receive_message(self, message: bytes) -> None:
            """
            Does something when receiving bytes

            Parameters
            ----------
            message : bytes
                A message as bytes

            Returns
            -------
            None:
                Alter state

            Raises
            ------
            RuntimeError
                Unreachable behaviour
            """
            return

        def on_expiration_time(self) -> None:
            """
            Behaviour on time expiration

            Returns
            -------
            None
            """
            return

    class ErrorState(State):
        """
        Error State, when reached next call is going to raise a RuntimeError
        """
        __name__ = "Error State"

        def receive_message(self, message: bytes) -> None:
            """
            Always raise RuntimeError

            Parameters
            ----------
            message : bytes
                Any message

            Returns
            -------
            None

            Raises
            ------
            SystemExit :
                Raises a SystemExit with error code -1
            """
            raise SystemExit(self.state_machine.__exit_msg__)

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
            SystemExit :
                Raises a SystemExit with error code -1
            """
            raise SystemExit(self.state_machine.__exit_msg__)

    class EndState(State):
        """
        End State, when reached next call is going to stop and exit
        """
        __name__ = "End State"

        def receive_message(self, message: bytes) -> None:
            """
            Always raise RuntimeError

            Parameters
            ----------
            message : bytes
                Any message

            Returns
            -------
            None

            Raises
            ------
            SystemExit :
                Raises a SystemExit with error code -1
            """
            raise SystemExit(self.state_machine.__end_msg__)

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
            SystemExit :
                Raises a SystemExit with error code -1
            """
            raise SystemExit(self.state_machine.__end_msg__)

    def __init__(self, protocol: SCHCProtocol, dtag: int = None) -> None:
        """
        Constructor

        Parameters
        ----------
        protocol : SCHCProtocol
            Protocol to use
        dtag : int, optional
            Dtag to identify behaviour, Default: -1 implying there is just
            one SCHC Packet for Rule ID at a time
        """
        self.protocol = protocol
        self.__rule_id__ = protocol.RULE_ID
        if protocol.T == 0:
            self.__dtag__ = None
        else:
            self.__dtag__ = dtag
        self.__current_window__ = 0
        self.__last_window__ = False
        self.__fcn__ = self.protocol.WINDOW_SIZE - 1
        self.bitmap = Bitmap(protocol)
        self.attempts = AttemptsCounter(protocol.MAX_ACK_REQUEST)
        self.states: Dict[str, SCHCFiniteStateMachine.State] = dict()
        self.states["error"] = SCHCFiniteStateMachine.ErrorState(self)
        self.states["end"] = SCHCFiniteStateMachine.EndState(self)
        self.state = SCHCFiniteStateMachine.State(self)
        self.rcs = ""
        self.__exit_msg__ = ""
        self.__end_msg__ = ""
        self.message_to_send: List[SCHCMessage] = list()
        return

    def receive_message(self, message: bytes) -> None:
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
        self.state.receive_message(message)
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
        SCHCMessage :
            SCHC Messages to send

        Raises
        ------
        RuntimeError
            No more SCHC Message to send on current state
        """
        return self.state.generate_message(mtu)

    def on_expiration_time(self, alarm: Timer) -> None:
        """
        Behaviour on time expiration

        Returns
        -------
        None
        """
        self.state.on_expiration_time()
        return
