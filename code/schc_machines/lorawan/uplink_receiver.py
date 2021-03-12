""" uplink_receiver: Uplink receiver state machine """

from __future__ import annotations

from typing import List

from schc_machines import SCHCReceiver, AckOnError
from schc_messages import RegularSCHCFragment, SCHCMessage, SCHCAck
from schc_protocols import SCHCProtocol


class UplinkReceiver(AckOnError, SCHCReceiver):
    """
    Uplink Receiver State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    """
    class ReceivingPhase(SCHCReceiver.ReceiverState, AckOnError):
        """
        Receiving Phase of Ack on Error
        """
        __name__ = "Receiving Phase"

        def __init__(self, state_machine: UplinkReceiver) -> None:
            super().__init__(state_machine)
            self.message_to_send: List[SCHCMessage] = list()

        def on_expiration_time(self) -> None:
            """
            Executed on expiration time

            Returns
            -------
            None, alter state to error
            """
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
            RuntimeError:
                No message to be send
            """
            if len(self.message_to_send) != 0:
                message = self.message_to_send.pop(0)
                if (message.size // 8) > mtu:
                    self.message_to_send.insert(0, message)
                    self._logger_.warning(
                        "Cannot send message, no bandwidth available. MTU = {} < Message size = {}".format(
                            mtu, message.size // 8
                        )
                    )
                self._logger_.schc_message(message)
                return message
            else:
                raise RuntimeError("No message to send, keep receiving")

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
            if self.state_machine.__last_window__:
                # TODO
                pass
            elif self.state_machine.__current_window__ == schc_message.header.w:
                self._logger_.debug("Window received: {}".format(schc_message.header.w.w))
                fcn = schc_message.header.fcn.fcn
                tiles_received = schc_message.payload.size // self.state_machine.protocol.TILE_SIZE
                tiles = schc_message.payload.as_bytes()
                self._logger_.debug("Tiles from: {} to {}".format(fcn, fcn - tiles_received + 1))
                for tile in range(tiles_received):
                    self.state_machine.payload.add_content(tiles[0:self.state_machine.protocol.TILE_SIZE // 8])
                    tiles = tiles[self.state_machine.protocol.TILE_SIZE // 8:]
                    self.state_machine.bitmap.tile_received(fcn - tile)
                    self.state_machine.__fcn__ -= 1
                    if self.state_machine.__fcn__ == -1:
                        self.message_to_send.append(
                            SCHCAck(self.state_machine.__rule_id__,
                                    self.state_machine.protocol.id,
                                    c=False,
                                    dtag=self.state_machine.__dtag__,
                                    w=self.state_machine.__current_window__,
                                    compressed_bitmap=self.state_machine.bitmap.generate_compress())
                        )
                        self.state_machine.__current_window__ -= 1
                        self.state_machine.__fcn__ = self.state_machine.protocol.WINDOW_SIZE - 1
                        self._logger_.debug("Current bitmap: {}".format(self.state_machine.bitmap))
                    self._logger_.debug("Current bitmap: {}".format(self.state_machine.bitmap))
            return

    class WaitingPhase(SCHCReceiver.ReceiverState, AckOnError):
        """
        Waiting Phase of Ack on Error
        """
        __name__ = "Waiting Phase"

    class WaitingEndPhase(SCHCReceiver.ReceiverState, AckOnError):
        """
        Waiting End Phase of Ack on Error
        """
        __name__ = "Waiting End Phase"

    def __init__(self, protocol: SCHCProtocol, dtag: int = None) -> None:
        super().__init__(protocol, dtag=dtag)
        AckOnError.__init__(self)
        self.states["receiving_phase"] = UplinkReceiver.ReceivingPhase(self)
        self.states["waiting_phase"] = UplinkReceiver.WaitingPhase(self)
        self.states["waiting_end_phase"] = UplinkReceiver.WaitingEndPhase(self)
        self.state = self.states["receiving_phase"]
        self.state.enter_state()
        return
