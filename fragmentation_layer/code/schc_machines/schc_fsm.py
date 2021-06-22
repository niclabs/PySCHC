""" schc_fsm: SCHC Finite State Machine Abstract Class """

import sys

if sys.implementation.name == "micropython":
    import time
    now = time.time
else:
    import datetime
    now = datetime.datetime.now

from machine import Timer
from schc_base import AttemptsCounter, Bitmap
from schc_messages import SCHCMessage
from schc_protocols import SCHCProtocol


class SCHCFiniteStateMachine:
    """
    Finite State Machine of Sender/Receiver (Fragmenter/Reassembler)
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
    __cw__ : int
        Current window being processed
    __last_window__ : bool
        Whether current window is the last window
    __fcn__ : int
        Current fcn in progress of window
    bitmaps : Dict[int, Bitmap]
        Bitmaps of all windows
    attempts : AttemptsCounter
        Attempts Counter that register request for SCHC ACKs
    state : State
        Current State of State Machine
    states: Dict[str, State]
        Possible States of FSM
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
        sm : SCHCFiniteStateMachine
            State Machine associated
        """
        __name__ = "State"

        class Logger:
            """
            SCHC Logger to log SCHC Fragmentation
            """
            TAG = "{mode}::[{datetime}]::"

            def __init__(self, state):
                self.__state__ = state
                return

            def __log__(self, mode):
                print(
                    self.TAG.format(mode=mode, datetime=now()) +
                    "SCHC Fragment on '{}' mode, {} on '{}' state".format(
                        self.__state__.sm.__mode__,
                        self.__state__.sm.__type__,
                        self.__state__.__name__
                ))
                second_line = "\tProtocol: {}, Rule ID: {}".format(
                    self.__state__.sm.protocol.__name__,
                    self.__state__.sm.__rule_id__
                )
                if self.__state__.sm.__dtag__ is not None:
                    second_line += ", DTag: {}".format(
                        self.__state__.sm.__dtag__
                    )
                print(second_line)
                return

            def enter_state(self):
                """
                Logs entering a new state

                Returns
                -------
                None
                """
                self.__log__("DEBUG")
                return

            def schc_message(self, message):
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
                print("\tMessage:\n{}".format(message.as_text()))
                return

            def error(self, message):
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
                self.__log__("ERROR")
                print("\t{}".format(message))
                return

            def warning(self, message):
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
                self.__log__("WARNING")
                print("\t{}".format(message))
                return

            def debug(self, message):
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
                self.__log__("DEBUG")
                print("\t{}".format(message))
                return

            def info(self, message):
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
                self.__log__("INFO")
                print("\t{}".format(message))
                return

        def __init__(self, state_machine):
            self.sm = state_machine
            self._logger_ = SCHCFiniteStateMachine.State.Logger(self)
            return

        def enter_state(self):
            """
            Logs enter on this state

            Returns
            -------
            None
            """
            self._logger_.enter_state()
            return

        def generate_message(self, mtu):
            """
            Message to send by default: Sends enqueue messages

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
            if len(self.sm.message_to_send) != 0:
                message = self.sm.message_to_send.pop(0)
                if (message.size // 8) > mtu:
                    self.sm.message_to_send.insert(0, message)
                    self._logger_.warning(
                        "Cannot send message, no bandwidth available. MTU = {} < Message size = {}".format(
                            mtu, message.size // 8
                        )
                    )
                self._logger_.schc_message(message)
                return message
            else:
                return None

        def receive_message(self, message):
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

        def on_expiration_time(self, alarm) -> None:
            """
            Behaviour on time expiration

            Parameters
            ----------
            alarm : Timer
                Alarm that triggers expiration

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

        def receive_message(self, message):
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
            raise SystemExit(self.sm.__exit_msg__)

        def generate_message(self, mtu):
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
            raise SystemExit(self.sm.__exit_msg__)

    class EndState(State):
        """
        End State, when reached next call is going to stop and exit
        """
        __name__ = "End State"

        def receive_message(self, message):
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
            raise SystemExit(self.sm.__end_msg__)

        def generate_message(self, mtu):
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
            raise SystemExit(self.sm.__end_msg__)

        def on_expiration_time(self, alarm) -> None:
            """
            Behaviour on time expiration

            Parameters
            ----------
            alarm : Timer
                Alarm that triggers expiration

            Returns
            -------
            None
            """
            self.sm.__active__ = False
            return

    def __init__(self, protocol, dtag=None):
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
        self.__cw__ = 0
        self.__last_window__ = False
        self.__fcn__ = self.protocol.WINDOW_SIZE - 1
        self.bitmaps = {
            self.__cw__: Bitmap(protocol),
        }
        self.attempts = AttemptsCounter(protocol.MAX_ACK_REQUEST)
        self.states = dict()
        self.states["error"] = SCHCFiniteStateMachine.ErrorState(self)
        self.states["end"] = SCHCFiniteStateMachine.EndState(self)
        self.state = SCHCFiniteStateMachine.State(self)
        self.rcs = ""
        self.__exit_msg__ = ""
        self.__end_msg__ = ""
        self.message_to_send = list()
        self.__active__ = True
        return

    def receive_message(self, message):
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

    def generate_message(self, mtu):
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

    def on_expiration_time(self, alarm):
        """
        Behaviour on time expiration

        Parameters
        ----------
        alarm : Timer
            Timer of machine that activates the alarm

        Returns
        -------
        None
        """
        self.state.on_expiration_time(alarm)
        return

    def is_active(self):
        return self.__active__
