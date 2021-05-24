""" ack_on_error_sender: AckOnError sender state machine """

from schc_base import Tile, Bitmap
from schc_machines import SCHCSender
from schc_messages import RegularSCHCFragment, All1SCHCFragment, SCHCAck, SCHCAckReq


class AckOnErrorSender(SCHCSender):
    """
    AckOnError Sender State Machine with Ack-on-Error Mode
    
    Attributes
    ----------
    protocol
    state
    residue
    """
    __mode__ = "Ack On Error"

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
            # MTU should not count FPort
            mtu_available += regular_message.header.rule_id.size
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
                        self.sm.message_to_send.append(SCHCAckReq(
                            self.sm.__rule_id__,
                            self.sm.protocol.id,
                            self.sm.__cw__,
                            self.sm.__dtag__
                        ))
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
                self.sm.message_to_send.append(SCHCAckReq(
                    self.sm.__rule_id__,
                    self.sm.protocol.id,
                    self.sm.__cw__,
                    self.sm.__dtag__
                ))
                all1.add_padding()
                return all1
            regular_message.add_padding()
            self._logger_.schc_message(regular_message)
            return regular_message

        def receive_schc_ack(self, schc_message):
            """
            Logs SCHC ACK

            Parameters
            ----------
            schc_message : SCHCAck
                Message received

            Returns
            -------
            None
            """
            self._logger_.debug("Received SCHC ACK. Ignoring.")

    class WaitingPhase(SCHCSender.SenderState):
        """
        Waiting Phase of Ack on Error
        """
        __name__ = "Waiting Phase"

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
                None
            """
            if len(self.sm.message_to_send) != 0:
                if self.sm.message_to_send[0].size - self.sm.protocol.FPORT_LENGTH <= mtu * 8:
                    message = self.sm.message_to_send.pop(0)
                    return message
            else:
                return None

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
            if self.sm.__cw__ != schc_message.header.w:
                # TODO
                return
            else:
                if schc_message.header.c.c:
                    if self.sm.__last_window__:
                        self.sm.state = self.sm.states["end"]
                        self.sm.state.enter_state()
                        return
                    else:
                        # TODO
                        return
                else:
                    self.sm.bitmap = Bitmap.from_compress_bitmap(
                        schc_message.header.compressed_bitmap.bitmap, self.sm.protocol)
                    self._logger_.debug("Received bitmap: {}".format(self.sm.bitmap))
                    if sum(self.sm.bitmap) == len(self.sm.bitmap):
                        self.sm.state = self.sm.states["sending_phase"]
                        self.sm.retransmission_timer.stop()
                        self.sm.__cw__ += 1
                        self.sm.__fcn__ = self.sm.protocol.WINDOW_SIZE - 1
                        self.sm.state.enter_state()
                        return
                    else:
                        # TODO
                        return

    def __init__(self, protocol, payload, padding=0, dtag=None):
        super().__init__(protocol, payload, padding=padding, dtag=dtag)
        self.states["initial_phase"] = AckOnErrorSender.InitialPhase(self)
        self.states["sending_phase"] = AckOnErrorSender.SendingPhase(self)
        self.states["waiting_phase"] = AckOnErrorSender.WaitingPhase(self)
        self.state = self.states["initial_phase"]
        self.state.enter_state()
        self.tiles = list()
        self.sent_tiles = list()
        self.state.__generate_tiles__()
        return
