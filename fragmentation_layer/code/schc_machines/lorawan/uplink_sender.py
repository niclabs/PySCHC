""" uplink_sender: Uplink sender state machine """

from schc_base import Tile, Bitmap
from schc_machines import SCHCSender, AckOnError
from schc_messages import SCHCMessage, RegularSCHCFragment, All1SCHCFragment, SCHCAck, SCHCSenderAbort, SCHCAckReq
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

        def __generate_tiles__(self):
            sm = self.sm
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
            self.sm.state = self.sm.states["sending_phase"]
            self.sm.state.enter_state()
            return

    class SendingPhase(SCHCSender.SenderState):
        """
        Sending Phase of Ack on Error
        """
        __name__ = "Sending Phase"

        def generate_message(self, mtu):
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
            regular_message = RegularSCHCFragment(self.sm.__rule_id__,
                                                  self.sm.__fcn__,
                                                  self.sm.protocol.id,
                                                  self.sm.__dtag__,
                                                  self.sm.__cw__)
            mtu_available = (mtu - (regular_message.size // 8)) * 8
            if len(self.sm.tiles) > 1:
                candid = self.sm.tiles[0]
                while mtu_available >= candid.size and len(self.sm.tiles) > 1:
                    regular_message.add_tile(candid)
                    self.sm.sent_tiles.append(
                        self.sm.tiles.pop(0)
                    )
                    mtu_available -= candid.size
                    candid = self.sm.tiles[0]
                    self._logger_.debug("Add tile with fcn {} for windows {}".format(
                        self.sm.__fcn__, self.sm.__cw__))
                    self.sm.__fcn__ -= 1
                    if self.sm.__fcn__ < 0:
                        self.sm.state = self.sm.states["waiting_phase"]
                        self.sm.retransmission_timer.reset()
                        self.sm.state.enter_state()
                        break
            else:
                last_tile = self.sm.tiles.pop(0)
                self.sm.sent_tiles.append(last_tile)
                self.sm.__last_window__ = True
                all1 = All1SCHCFragment(
                    self.sm.__rule_id__,
                    self.sm.protocol.id,
                    self.sm.__dtag__,
                    self.sm.__cw__,
                    self.sm.rcs
                )
                all1.add_tile(last_tile)
                self._logger_.schc_message(all1)
                self.sm.state = self.sm.states["waiting_phase"]
                self.sm.state.enter_state()
                self.sm.retransmission_timer.reset()
                all1.add_padding()
                return all1
            regular_message.add_padding()
            self._logger_.schc_message(regular_message)
            return regular_message

    class ResendingPhase(SCHCSender.SenderState):
        """
        Resending missing tiles State
        """
        __name__ = "Resending Phase"

        def generate_message(self, mtu):
            """
            Sends fragments reported missing

            Parameters
            ----------
            mtu : int
                Current mtu

            Returns
            -------
            RegularSCHCFragment :
                Message with missing tiles
            """
            self._logger_.debug("\n".join([str(tile) for tile in self.sm.sent_tiles]))
            self._logger_.debug("Tiles in sent tiles: {}".format(len(self.sm.sent_tiles)))
            bitmap = self.sm.bitmaps[self.sm.__cw__]
            self.sm.__fcn__ = self.sm.protocol.WINDOW_SIZE - 1 - bitmap.get_missing()
            regular_message = RegularSCHCFragment(self.sm.__rule_id__,
                                                  self.sm.__fcn__,
                                                  self.sm.protocol.id,
                                                  self.sm.__dtag__,
                                                  self.sm.__cw__)
            mtu_available = (mtu - (regular_message.size // 8)) * 8
            candid = self.sm.sent_tiles[bitmap.get_missing()]
            while mtu_available > candid.size:
                regular_message.add_tile(candid)
                bitmap.tile_received(self.sm.__fcn__)
                mtu_available -= candid.size
                if bitmap.is_missing():
                    self.sm.__fcn__ = self.sm.protocol.WINDOW_SIZE - 1 - bitmap.get_missing()
                    candid = self.sm.sent_tiles[bitmap.get_missing()]
                else:
                    self.sm.state = self.sm.states["waiting_phase"]
                    self.sm.retransmission_timer.reset()
                    self.sm.state.enter_state()
                    self.sm.message_to_send.append(
                        SCHCAckReq(self.sm.__rule_id__, self.sm.protocol.id,
                                   w=self.sm.__cw__)
                    )
                    break
            return regular_message

    class WaitingPhase(SCHCSender.SenderState):
        """
        Waiting Phase of Ack on Error
        """
        __name__ = "Waiting Phase"

        def __init__(self, state_machine):
            super().__init__(state_machine)
            self.pending_state = list()
            return

        def generate_message(self, mtu):
            """
            Wait for ACK

            Parameters
            ----------
            mtu : int
                MTU in bytes

            Returns
            -------
            SCHCMessage :
                SCHCMessage on message_to_sent. Can be SCHCSenderAbort or SCHCAckReq

            Raises
            ------
            GeneratorExit
                Awaits for Ack
            """
            if len(self.sm.message_to_send) != 0:
                message = self.sm.message_to_send.pop(0)
                self._logger_.schc_message(message)
                if len(self.sm.message_to_send) == 0 and len(self.pending_state) != 0:
                    self.sm.state = self.pending_state.pop(0)
                return message
            else:
                raise GeneratorExit("Awaits for Ack after a windows was sent")

        def receive_schc_ack(self, schc_message):
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
            w = schc_message.header.w.w
            bitmap = Bitmap.from_compress_bitmap(
                schc_message.header.compressed_bitmap.bitmap, self.sm.protocol)
            self._logger_.debug("Received bitmap: {} with W={}".format(bitmap, w))
            # if self.sm.__cw__ != w:
            #     # TODO
            #     return
            # else:
            self.sm.bitmaps[w] = bitmap
            if self.sm.__last_window__:
                if schc_message.header.c.c:
                    self.sm.state = self.sm.states["end"]
                    self.sm.state.enter_state()
                    return
                else:
                    return
            else:
                if bitmap.is_missing():
                    self.sm.state = self.sm.states["resending_phase"]
                    self.sm.retransmission_timer.stop()
                    self.sm.__cw__ = w
                    self.sm.state.enter_state()
                else:
                    self.sm.message_to_send.append(SCHCSenderAbort(
                        self.sm.__rule_id__, self.sm.protocol.id,
                        w=self.sm.__cw__))
                    self.pending_state = [self.sm.states["error"]]
                    return
                # if sum(self.sm.bitmap) == len(self.sm.bitmap):
                #     self.sm.state = self.sm.states["sending_phase"]
                #     self.sm.retransmission_timer.stop()
                #     self.sm.__cw__ += 1
                #     self.sm.__fcn__ = self.sm.protocol.WINDOW_SIZE - 1
                #     self.sm.state.enter_state()
                # else:
                #
                #         return

    def __init__(self, protocol, payload, residue="", dtag=None):
        super().__init__(protocol, payload, residue=residue, dtag=dtag)
        AckOnError.__init__(self)
        self.states["initial_phase"] = UplinkSender.InitialPhase(self)
        self.states["sending_phase"] = UplinkSender.SendingPhase(self)
        self.states["resending_phase"] = UplinkSender.ResendingPhase(self)
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
