""" uplink_receiver: Uplink receiver state machine """

from __future__ import annotations
from typing import List
from schc_base import Bitmap
from schc_machines import SCHCReceiver, AckOnError
from schc_messages import SCHCMessage, RegularSCHCFragment, SCHCAck, All1SCHCFragment
from schc_protocols import SCHCProtocol


class UplinkReceiver(AckOnError, SCHCReceiver):
    """
    Uplink Receiver State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    """
    class ReceivingPhase(SCHCReceiver.ReceiverState):
        """
        Receiving Phase of Ack on Error

        Attributes
        ----------
        __success__ : bool
            Whether message was receive
        """
        __name__ = "Receiving Phase"

        def __init__(self, state_machine: UplinkReceiver) -> None:
            super().__init__(state_machine)
            self.__success__ = False

        def on_expiration_time(self) -> None:
            """
            Executed on expiration time

            Returns
            -------
            None, alter state to error
            """
            self.state_machine.__exit_msg__ = "Connection timeout"
            self.state_machine.state = self.state_machine.states["error"]
            self.state_machine.state.enter_state()
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Send messages saved on message_to_send variable

            Parameters
            ----------
            mtu : int
                MTU available

            Returns
            -------
            SCHCMessage :
                A message saved to be send

            Raises
            ------
            GeneratorExit
                No message to be send
            """
            if self.state_machine.__last_window__ and self.__success__:
                self.state_machine.state = self.state_machine.states["end"]
                self.state_machine.state.enter_state()
                message = self.state_machine.message_to_send.pop(0)
                self._logger_.schc_message(message)
                return message
            raise GeneratorExit("No message to send, keep receiving")

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> None:
            """

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                A regular Fragment received

            Returns
            -------
            None, alter state
            """
            if self.state_machine.__current_window__ == schc_message.header.w:
                fcn = schc_message.header.fcn.fcn
                self.state_machine.__fcn__ = fcn
                tiles_received = schc_message.payload.size // self.state_machine.protocol.TILE_SIZE
                tiles = schc_message.payload.as_bytes()
                self._logger_.debug("Window received: {}\tTiles from: {} to {}".format(
                    schc_message.header.w.w, fcn, fcn - tiles_received + 1))
                for tile in range(tiles_received):
                    self.state_machine.payload.add_content(tiles[0:self.state_machine.protocol.TILE_SIZE // 8])
                    tiles = tiles[self.state_machine.protocol.TILE_SIZE // 8:]
                    self.state_machine.bitmap.tile_received(fcn - tile)
                    self.state_machine.__fcn__ -= 1
                    if self.state_machine.__fcn__ == -1:
                        ack = SCHCAck(self.state_machine.__rule_id__,
                                      self.state_machine.protocol.id, c=False,
                                      dtag=self.state_machine.__dtag__,
                                      w=self.state_machine.__current_window__,
                                      compressed_bitmap=self.state_machine.bitmap.generate_compress())
                        ack.add_padding()
                        self.state_machine.message_to_send.append(ack)
                        self.state_machine.state = self.state_machine.states["waiting_phase"]
                        self.state_machine.state.enter_state()
                        return
                self._logger_.debug("Current bitmap: {}. Waiting for w={} fcn={} tile".format(
                    self.state_machine.bitmap, self.state_machine.__current_window__, self.state_machine.__fcn__)
                )
            else:
                self._logger_.debug("Different window received")
            return

        def receive_all1_schc_fragment(self, schc_message: All1SCHCFragment) -> None:
            """
            Behaviour of when receiving All-1 SCHC Fragment

            Parameters
            ----------
            schc_message : All1SCHCFragment
                Last fragment to be received

            Returns
            -------
            None, alter state
            """
            if self.state_machine.__current_window__ == schc_message.header.w:
                self.state_machine.__last_window__ = True
                last_payload = schc_message.payload.as_bytes()
                self.state_machine.payload.add_content(last_payload)
                rcs = self.state_machine.protocol.calculate_rcs(
                    self.state_machine.payload.as_bits()
                )
                integrity = rcs == schc_message.header.rcs.rcs
                if integrity:
                    self._logger_.debug("Integrity check successful")
                    compressed_bitmap = None
                    self.__success__ = True
                else:
                    self._logger_.error("Integrity check failed:\tSender: {}\tReceiver:{}".format(
                        schc_message.header.rcs.rcs,
                        rcs
                    ))
                    compressed_bitmap = self.state_machine.bitmap.generate_compress()
                ack = SCHCAck(self.state_machine.__rule_id__,
                              self.state_machine.protocol.id,
                              c=integrity,
                              dtag=self.state_machine.__dtag__,
                              w=self.state_machine.__current_window__,
                              compressed_bitmap=compressed_bitmap)
                ack.add_padding()
                self.state_machine.message_to_send.append(ack)
                return
            else:
                # TODO
                return

    class WaitingPhase(SCHCReceiver.ReceiverState):
        """
        Waiting Phase of Ack on Error
        """
        __name__ = "Waiting Phase"

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Send an SCHCAcK
            Parameters
            ----------
            mtu : int
                Current mtu

            Returns
            -------
            SCHCMessage :
                Message to send
            """
            if len(self.state_machine.message_to_send) != 0:
                message = self.state_machine.message_to_send.pop(0)
                if (message.size // 8) > mtu:
                    self.state_machine.message_to_send.insert(0, message)
                    self._logger_.warning(
                        "Cannot send message, no bandwidth available. MTU = {} < Message size = {}".format(
                            mtu, message.size // 8
                        )
                    )
                self._logger_.schc_message(message)
                return message
            else:
                raise GeneratorExit("No message to send, keep receiving")

        def receive_regular_schc_fragment(self, schc_message: RegularSCHCFragment) -> None:
            """
            Receiving a regular SCHC Fragment to start new window

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                First regular sent of a new window

            Returns
            -------
            None, alter state
            """
            if schc_message.header.w != self.state_machine.__current_window__:
                self.state_machine.__current_window__ = schc_message.header.w.w
                self._logger_.debug("Starting reception of window {}".format(
                    self.state_machine.__current_window__))
                self.state_machine.bitmap = Bitmap(self.state_machine.protocol)
                self.state_machine.state = self.state_machine.states["receiving_phase"]
                self.enter_state()
                self.state_machine.state.receive_regular_schc_fragment(schc_message)
            else:
                # TODO
                pass
            return

    def __init__(self, protocol: SCHCProtocol, dtag: int = None) -> None:
        super().__init__(protocol, dtag=dtag)
        AckOnError.__init__(self)
        self.states["receiving_phase"] = UplinkReceiver.ReceivingPhase(self)
        self.states["waiting_phase"] = UplinkReceiver.WaitingPhase(self)
        self.state = self.states["receiving_phase"]
        self.inactivity_timer.stop()
        self.state.enter_state()
        return
