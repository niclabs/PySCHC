""" ack_on_error_receiver: AckOnError receiver state machine """

from machine import Timer
from schc_base import Bitmap
from schc_machines import SCHCReceiver
from schc_messages import RegularSCHCFragment, SCHCAck, All1SCHCFragment, SCHCAckReq


class AckOnErrorReceiver(SCHCReceiver):
    """
    AckOnError Receiver State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    """
    __mode__ = "Ack On Error"

    class ReceivingPhase(SCHCReceiver.ReceiverState):
        """
        Receiving Phase of Ack on Error

        Attributes
        ----------
        __success__ : bool
            Whether message was receive
        """
        __name__ = "Receiving Phase"

        def __init__(self, state_machine):
            super().__init__(state_machine)
            self.__success__ = False

        def on_expiration_time(self, alarm):
            """
            Executed on expiration time

            Parameters
            ----------
            alarm : Timer
                Timer that triggers expiration

            Returns
            -------
            None, alter state to error
            """
            self.sm.__exit_msg__ = "Connection timeout"
            self.sm.state = self.sm.states["error"]
            self.sm.state.enter_state()
            return

        def generate_message(self, mtu):
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
            """
            if self.sm.__last_window__ and self.__success__:
                self.sm.state = self.sm.states["end"]
                self.sm.state.enter_state()
                message = self.sm.message_to_send.pop(0)
                self._logger_.schc_message(message)
                self.sm.on_success(self.sm.payload.as_bytes())
                return message
            else:
                return None

        def receive_regular_schc_fragment(self, schc_message):
            """

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                A regular Fragment received

            Returns
            -------
            None, alter state
            """
            if self.sm.__cw__ == schc_message.header.w:
                fcn = schc_message.header.fcn.fcn
                self.sm.__fcn__ = fcn
                tiles_received = schc_message.payload.size // self.sm.protocol.TILE_SIZE
                tiles = schc_message.payload.as_bytes()
                self._logger_.debug("Window received: {}\tTiles from: {} to {}".format(
                    schc_message.header.w.w, fcn, fcn - tiles_received + 1))
                for tile in range(tiles_received):
                    self.sm.payload.add_content(tiles[0:self.sm.protocol.TILE_SIZE // 8])
                    tiles = tiles[self.sm.protocol.TILE_SIZE // 8:]
                    self.sm.bitmaps[
                        self.sm.__cw__
                    ].tile_received(fcn - tile)
                    self.sm.__fcn__ -= 1
                    if self.sm.__fcn__ == -1:
                        ack = SCHCAck(self.sm.__rule_id__,
                                      self.sm.protocol.id, c=False,
                                      dtag=self.sm.__dtag__,
                                      w=self.sm.__cw__,
                                      compressed_bitmap=self.sm.bitmaps[
                                          self.sm.__cw__
                                      ].generate_compress())
                        ack.add_padding()
                        self.sm.message_to_send.append(ack)
                        self.sm.state = self.sm.states["waiting_phase"]
                        self.sm.state.enter_state()
                        return
                self._logger_.debug("Current bitmap: {}. Waiting for w={} fcn={} tile".format(
                    self.sm.bitmaps[
                        self.sm.__cw__
                    ], self.sm.__cw__, self.sm.__fcn__)
                )
            else:
                self._logger_.debug("Different window received")
            return

        def receive_all1_schc_fragment(self, schc_message):
            """
            Behaviour when receiving All-1 SCHC Fragment

            Parameters
            ----------
            schc_message : All1SCHCFragment
                Last fragment to be received

            Returns
            -------
            None, alter state
            """
            if self.sm.__cw__ == schc_message.header.w:
                self.sm.__last_window__ = True
                last_payload = schc_message.payload.as_bytes()
                self.sm.payload.add_content(last_payload)
                rcs = self.sm.protocol.calculate_rcs(
                    self.sm.payload.as_bits()
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
                    compressed_bitmap = self.sm.bitmaps[
                        self.sm.__cw__
                    ].generate_compress()
                ack = SCHCAck(self.sm.__rule_id__,
                              self.sm.protocol.id,
                              c=integrity,
                              dtag=self.sm.__dtag__,
                              w=self.sm.__cw__,
                              compressed_bitmap=compressed_bitmap)
                ack.add_padding()
                self.sm.message_to_send.append(ack)
                return
            else:
                # TODO
                return

        def receive_schc_ack_req(self, schc_message):
            """
            Behaviour when receiving a SCHCAck Request

            Parameters
            ----------
            schc_message : SCHCAckReq
                Message requesting an Ack

            Returns
            -------
            None, alter state
            """
            for w in sorted(self.sm.bitmaps.keys()):
                bitmap = self.sm.bitmaps[w]
                if bitmap.is_missing():
                    self._logger_.debug("Window {} has missing tiles".format(w))
                    self.sm.message_to_send.append(
                        SCHCAck(self.sm.__rule_id__, self.sm.protocol.id,
                                False, w=w, compressed_bitmap=bitmap.generate_compress())
                    )
                    return
            bitmap = self.sm.bitmaps[self.sm.__cw__]
            self.sm.message_to_send.append(
                SCHCAck(self.sm.__rule_id__, self.sm.protocol.id,
                        False, w=self.sm.__cw__, compressed_bitmap=bitmap.generate_compress())
            )
            return

    class WaitingPhase(SCHCReceiver.ReceiverState):
        """
        Waiting Phase of Ack on Error
        """
        __name__ = "Waiting Phase"

        def generate_message(self, mtu):
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

        def receive_regular_schc_fragment(self, schc_message):
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
            if schc_message.header.w != self.sm.__cw__:
                self.sm.__cw__ = schc_message.header.w.w
                self._logger_.debug("Starting reception of window {}".format(
                    self.sm.__cw__))
                self.sm.bitmaps[self.sm.__cw__] = Bitmap(self.sm.protocol)
                self.sm.state = self.sm.states["receiving_phase"]
                self.enter_state()
                self.sm.state.receive_regular_schc_fragment(schc_message)
            else:
                self._logger_.debug("Receiving failed ones")
                fcn = schc_message.header.fcn.fcn
                tiles_received = schc_message.payload.size // self.sm.protocol.TILE_SIZE
                tiles = schc_message.payload.as_bytes()
                for tile in range(tiles_received):
                    self._logger_.debug("Window received: {}\tTile {}".format(
                        schc_message.header.w.w, fcn))
                    self.sm.payload.add_content(tiles[0:self.sm.protocol.TILE_SIZE // 8])
                    tiles = tiles[self.sm.protocol.TILE_SIZE // 8:]
                    self.sm.bitmaps[self.sm.__cw__].tile_received(fcn)
                    if self.sm.bitmaps[self.sm.__cw__].is_missing():
                        fcn = self.sm.bitmaps[self.sm.__cw__].get_missing(fcn=True)
                    else:
                        break
            return

        def receive_schc_ack_req(self, schc_message):
            """
            Behaviour when SCHC Ack Request

            Parameters
            ----------
            schc_message : SCHCAckReq
                SCHC message received

            Returns
            -------
            None, alter state
            """
            w = schc_message.header.w.w
            if w not in self.sm.bitmaps.keys():
                return
            if not self.sm.__last_window__:
                self.sm.message_to_send.append(
                    SCHCAck(self.sm.__rule_id__, self.sm.protocol.id,
                            c=False, w=w, compressed_bitmap=self.sm.bitmaps[w].generate_compress())
                )
            else:
                pass
            return

    def __init__(self, protocol, dtag=None, on_success=None):
        super().__init__(protocol, dtag=dtag)
        self.states["receiving_phase"] = AckOnErrorReceiver.ReceivingPhase(self)
        self.states["waiting_phase"] = AckOnErrorReceiver.WaitingPhase(self)
        self.state = self.states["receiving_phase"]
        self.inactivity_timer.stop()
        self.state.enter_state()
        self.on_success = on_success
        return
