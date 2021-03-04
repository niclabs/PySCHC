""" schc_sender: SCHC Ack-on-Error Mode Sender Finite State Machine """

from __future__ import annotations
from schc_base import Tile
from schc_messages import SCHCMessage, SCHCAck, SCHCReceiverAbort, RegularSCHCFragment, All1SCHCFragment
from schc_messages.schc_header import WField
from schc_modes import SCHCSender
from schc_protocols import SCHCProtocol


class AckOnErrorSCHCSender(SCHCSender):
    """
    SCHC Finite State Machine for Ack On Error Sender behaviour

    Attributes
    ----------
    protocol
    state
    residue
    init_state
    sending_state
    waiting_state
    """
    class InitialPhase(SCHCSender.InitialPhase):
        """
        Initial Phase of Ack on Error
        """
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
            self.state_machine.state = self.state_machine.sending_state
            self.state_machine.state.enter_state()
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            pass

    class SendingPhase(SCHCSender.SendingPhase):
        """
        Sending Phase of Ack on Error
        """
        def generate_message(self, mtu: int) -> SCHCMessage:
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
                    self.state_machine.__fcn__ -= 1
                    if self.state_machine.__fcn__ < 0:
                        self.state_machine.__current_window__ += 1
                        self.state_machine.__fcn__ = self.state_machine.protocol.WINDOW_SIZE - 1
            elif len(self.state_machine.tiles) == 1:
                last_tile = self.state_machine.tiles.pop(0)
                regular_message.add_tile(last_tile)
                self.state_machine.sent_tiles.append(last_tile)
                self.state_machine.__last_window__ = True
            else:
                all1 = All1SCHCFragment(
                    self.state_machine.__rule_id__,
                    self.state_machine.protocol.id,
                    self.state_machine.__dtag__,
                    self.state_machine.__current_window__,
                    self.state_machine.rcs
                )
                self.state_machine.state = self.state_machine.waiting_state
                self.state_machine.retransmission_timer.reset()
                return all1
            regular_message.header.w = WField(self.state_machine.__current_window__,
                                              self.state_machine.protocol.M)
            regular_message.add_padding()
            self._logger_.schc_message(regular_message)
            return regular_message

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            pass

    class WaitingPhase(SCHCSender.WaitingPhase):
        """
        Waiting Phase of Ack on Error
        """
        def generate_message(self, mtu: int) -> SCHCMessage:
            pass

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            pass

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            pass

    def __init__(self, protocol: SCHCProtocol, rule_id: int, payload: bytes,
                 residue: str = "", dtag: int = None) -> None:
        super().__init__(protocol, rule_id, payload, residue=residue, dtag=dtag)
        self.__mode__ = "Ack On Error"
        self.init_state = AckOnErrorSCHCSender.InitialPhase(self)
        self.sending_state = AckOnErrorSCHCSender.SendingPhase(self)
        self.waiting_state = AckOnErrorSCHCSender.WaitingPhase(self)
        self.state = self.init_state
        self.state.enter_state()
        self.__fcn__ = self.protocol.WINDOW_SIZE - 1
        self.__last_window__ = False
        self.tiles = list()
        self.sent_tiles = list()
        self.state.__generate_tiles__()
        return
