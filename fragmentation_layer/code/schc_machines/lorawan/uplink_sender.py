""" uplink_sender: Uplink sender state machine """

from __future__ import annotations

from typing import Iterator

from schc_base import Tile, Bitmap
from schc_machines import SCHCSender, AckOnError
from schc_messages import SCHCMessage, RegularSCHCFragment, All1SCHCFragment, SCHCAck
from schc_messages.schc_header import WField
from schc_protocols import SCHCProtocol


class UplinkSender(AckOnError, SCHCSender):
    """
    Uplink Sender State Machine with Ack-on-Error Mode
    Attributes
    ----------
    protocol
    state
    residue
    """
    class InitialPhase(SCHCSender.SenderState):
        """
        Initial Phase of Ack on Error
        """
        __name__ = "Initial Phase"

        def __generate_tiles__(self) -> None:
            sm = self.state_machine
            last_tile_length = len(sm.remaining_packet) % sm.protocol.TILE_SIZE
            last_tile = sm.remaining_packet[-last_tile_length:]
            sm.remaining_packet = sm.remaining_packet[0:-last_tile_length]
            penultimate_tile = sm.remaining_packet[-sm.protocol.penultimate_tile():]
            sm.remaining_packet = sm.remaining_packet[0:-sm.protocol.penultimate_tile()]
            sm.tiles = [
                sm.remaining_packet[i*sm.protocol.TILE_SIZE:(i + 1)*sm.protocol.TILE_SIZE]
                for i in range(int(
                    len(sm.remaining_packet) // sm.protocol.TILE_SIZE
                ))
            ]
            assert "".join(sm.tiles) == sm.remaining_packet, "Error occur during Tile generation"
            sm.remaining_packet = list()
            sm.tiles.append(penultimate_tile)
            sm.tiles.append(last_tile)
            sm.tiles = [Tile(i) for i in sm.tiles]
            self._logger_.debug("{} tiles generated".format(len(sm.tiles)))
            self.state_machine.state = self.state_machine.states["sending_phase"]
            self.state_machine.state.enter_state()
            return

    class SendingPhase(SCHCSender.SenderState):
        """
        Sending Phase of Ack on Error
        """
        __name__ = "Sending Phase"

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Generate regular fragment until all tiles are sent

            Parameters
            ----------
            mtu : int
                MTU in bytes

            Returns
            -------
            SCHCMessage :
                RegularSCHCFragment until all tiles are sent, then
                All1SCHCFragment
            """
            regular_message = RegularSCHCFragment(self.state_machine.__rule_id__,
                                                  self.state_machine.__fcn__,
                                                  self.state_machine.protocol.id,
                                                  self.state_machine.__dtag__,
                                                  self.state_machine.__current_window__)
            mtu_available = (mtu - (regular_message.size // 8)) * 8
            if len(self.state_machine.tiles) > 1:
                candid = self.state_machine.tiles[0]
                while mtu_available >= candid.size and len(self.state_machine.tiles) > 1:
                    regular_message.add_tile(candid)
                    self.state_machine.sent_tiles.append(
                        self.state_machine.tiles.pop(0)
                    )
                    mtu_available -= candid.size
                    candid = self.state_machine.tiles[0]
                    self._logger_.debug("Add tile with fcn {} for windows {}".format(
                        self.state_machine.__fcn__, self.state_machine.__current_window__))
                    self.state_machine.__fcn__ -= 1
                    if self.state_machine.__fcn__ < 0:
                        self.state_machine.state = self.state_machine.states["waiting_phase"]
                        self.state_machine.retransmission_timer.reset()
                        self.state_machine.state.enter_state()
                        break
            else:
                last_tile = self.state_machine.tiles.pop(0)
                self.state_machine.sent_tiles.append(last_tile)
                self.state_machine.__last_window__ = True
                all1 = All1SCHCFragment(
                    self.state_machine.__rule_id__,
                    self.state_machine.protocol.id,
                    self.state_machine.__dtag__,
                    self.state_machine.__current_window__,
                    self.state_machine.rcs
                )
                all1.add_tile(last_tile)
                self._logger_.schc_message(all1)
                self.state_machine.state = self.state_machine.states["waiting_phase"]
                self.state_machine.state.enter_state()
                self.state_machine.retransmission_timer.reset()
                all1.add_padding()
                return all1
            regular_message.add_padding()
            self._logger_.schc_message(regular_message)
            return regular_message

    class WaitingPhase(SCHCSender.SenderState):
        """
        Waiting Phase of Ack on Error
        """
        __name__ = "Waiting Phase"

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Wait for ACK

            Parameters
            ----------
            mtu : int
                MTU in bytes

            Returns
            -------
            SCHCMessage :
                None

            Raises
            ------
            GeneratorExit
                Awaits for Ack
            """
            raise GeneratorExit("Awaits for Ack after a windows was sent")

        def receive_schc_ack(self, schc_message: SCHCAck) -> None:
            """
            Receive an Ack after a windows is fully sent

            Parameters
            ----------
            schc_message : SCHCAck
                SCHCAck reporting end of transmission or window

            Returns
            -------
            None, alter state
            """
            if self.state_machine.__current_window__ != schc_message.header.w:
                # TODO
                return
            else:
                if schc_message.header.c.c:
                    if self.state_machine.__last_window__:
                        self.state_machine.state = self.state_machine.states["end"]
                        self.state_machine.state.enter_state()
                        return
                    else:
                        # TODO
                        return
                else:
                    self.state_machine.bitmap = Bitmap.from_compress_bitmap(
                        schc_message.header.compressed_bitmap.bitmap, self.state_machine.protocol)
                    self._logger_.debug("Received bitmap: {}".format(self.state_machine.bitmap))
                    if sum(self.state_machine.bitmap) == len(self.state_machine.bitmap):
                        self.state_machine.state = self.state_machine.states["sending_phase"]
                        self.state_machine.retransmission_timer.stop()
                        self.state_machine.__current_window__ += 1
                        self.state_machine.__fcn__ = self.state_machine.protocol.WINDOW_SIZE - 1
                        self.state_machine.state.enter_state()
                        return
                    else:
                        # TODO
                        return

    def __init__(self, protocol: SCHCProtocol, payload: bytes,
                 residue: str = "", dtag: int = None) -> None:
        super().__init__(protocol, payload, residue=residue, dtag=dtag)
        self.states["initial_phase"] = UplinkSender.InitialPhase(self)
        self.states["sending_phase"] = UplinkSender.SendingPhase(self)
        self.states["waiting_phase"] = UplinkSender.WaitingPhase(self)
        self.state = self.states["initial_phase"]
        self.state.enter_state()
        if len(self.remaining_packet) % self.protocol.L2_WORD != 0:
            padding = "0" * (self.protocol.L2_WORD - (len(self.remaining_packet) % self.protocol.L2_WORD))
            self.rcs = self.protocol.calculate_rcs(self.remaining_packet + padding)
        self.tiles = list()
        self.sent_tiles = list()
        self.state.__generate_tiles__()
        return
