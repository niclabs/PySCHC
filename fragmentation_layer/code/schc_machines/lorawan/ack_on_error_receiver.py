""" ack_on_error_receiver: AckOnError receiver state machine """

from lopy_machine import Timer
from schc_base import Bitmap, Tile
from schc_machines import SCHCReceiver
from schc_messages import RegularSCHCFragment, SCHCAck, All1SCHCFragment, SCHCAckReq, SCHCReceiverAbort


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
                self.sm.inactivity_timer.reset()
                self.sm.on_success(self.sm.payload.as_bytes())
                if len(self.sm.message_to_send) > 0:
                    message = self.sm.message_to_send.pop(0)
                    self._logger_.schc_message(message)
                    return message
                else:
                    ack = SCHCAck(
                        rule_id=self.sm.__rule_id__,
                        protocol=self.sm.protocol.id,
                        c=True,
                        dtag=self.sm.__dtag__,
                        w=self.sm.__cw__
                    )
                    ack.add_padding()
                    return ack
            else:
                return None

        def on_expiration_time(self, alarm) -> None:
            """
            On expiration time behaviour for this phase

            Parameters
            ----------
            alarm : Timer
                Timer ofg machine that activates the alarm

            Returns
            -------
            None
            """
            std_on_expiration_time(self, alarm)
            return

        def receive_regular_schc_fragment(self, schc_message):
            """
            Behaviour when receiving a Regular SCHC Fragment

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                A regular Fragment received

            Returns
            -------
            None, alter state
            """
            self.sm.inactivity_timer.stop()
            if self.sm.__cw__ == schc_message.header.w:
                fcn = schc_message.header.fcn.fcn
                self.sm.__fcn__ = fcn
                tiles_received = schc_message.payload.size // self.sm.protocol.TILE_SIZE
                tiles = schc_message.payload.as_bytes()
                self._logger_.debug("Window received: {}\tTiles from: {} to {}".format(
                    schc_message.header.w.w, fcn, fcn - tiles_received + 1))
                for tile in range(tiles_received):
                    self.sm.add_tile(Tile(
                        tiles[0:self.sm.protocol.TILE_SIZE // 8]
                    ), w=self.sm.__cw__, fcn=self.sm.__fcn__)
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
                        self.sm.attempts.increment()
                        self.sm.state = self.sm.states["waiting_phase"]
                        self.sm.state.enter_state()
                        self.sm.inactivity_timer.reset()
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
                self.sm.add_tile(Tile(last_payload), w=self.sm.__cw__, fcn=self.sm.__fcn__)
                bitmap = self.sm.bitmaps[schc_message.header.w.w]
                if bitmap.has_missing():
                    integrity = False
                    compressed_bitmap = bitmap.generate_compress()
                else:
                    self.sm.reassemble()
                    rcs = self.sm.protocol.calculate_rcs(
                        self.sm.payload.as_bits()
                    )
                    integrity = rcs == schc_message.header.rcs.rcs
                    if integrity:
                        self._logger_.debug("Integrity check successful")
                        compressed_bitmap = None
                        self.__success__ = True
                    else:
                        self._logger_.error("Integrity check failed:\tSender: {}\tReceiver: {}".format(
                            schc_message.header.rcs.rcs,
                            rcs
                        ))
                        abort = SCHCReceiverAbort(
                            rule_id=self.sm.__rule_id__,
                            protocol=self.sm.protocol.id,
                            dtag=self.sm.__dtag__,
                            w=self.sm.__cw__
                        )
                        abort.add_padding()
                        self.sm.message_to_send.append(abort)
                        self.sm.state = self.sm.states["error"]
                        self.sm.state.enter_state()
                        return
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
                self._logger_.debug("(All-1) Different window received")
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
            w = schc_message.header.w.w
            if self.sm.__cw__ == w:
                try:
                    bitmap = self.sm.bitmaps[w]
                except KeyError:
                    self._logger_.warning("W is not valid: w received: {}".format(w))
                    return
            elif self.sm.__cw__ > w:
                self._logger_.warning(
                    "SCHCAckReq is for a completed window (current w={} > {}). Discarding message".format(
                        self.sm.__cw__, w))
                return
            else:  # self.sm.__cw__ < w:
                self._logger_.warning("Incorrect window, discarding")
                return
            if bitmap.is_missing():
                self._logger_.debug("Window {} has missing tiles".format(w))
                self.sm.state = self.sm.states["waiting_phase"]
                self.sm.state.enter_state()
                self.sm.inactivity_timer.reset()
            self.sm.message_to_send.append(
                SCHCAck(self.sm.__rule_id__, self.sm.protocol.id,
                        False, w=w, compressed_bitmap=bitmap.generate_compress())
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
            return super().generate_message(mtu)

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
                self.sm.__cw__ = schc_message.header.w.w
                self.sm.state = self.sm.states["receiving_missing_phase"]
                self.enter_state()
                self.sm.state.receive_regular_schc_fragment(schc_message)
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
            self.sm.state = self.sm.states["receiving_phase"]
            self.sm.state.enter_state()
            self.sm.state.receive_all1_schc_fragment(schc_message)
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
            ack = SCHCAck(
                rule_id=self.sm.__rule_id__,
                protocol=self.sm.protocol.id,
                c=False,
                w=w,
                compressed_bitmap=self.sm.bitmaps[w].generate_compress()
            )
            ack.add_padding()
            self.sm.message_to_send.append(ack)
            self.sm.attempts.increment()
            return

        def on_expiration_time(self, alarm) -> None:
            """
            On expiration time behaviour for this phase

            Parameters
            ----------
            alarm : Timer
                Timer of machine that activates the alarm

            Returns
            -------
            None
            """
            std_on_expiration_time(self, alarm)
            return

    class ReceivingMissingPhase(SCHCReceiver.ReceiverState):
        """
        Receiving Missing Phase, machine receive missing fragments
        """
        __name__ = "Receiving Missing Phase"

        def receive_regular_schc_fragment(self, schc_message):
            """
            Behaviour when receiving a Regular SCHC Fragment

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                A regular Fragment received

            Returns
            -------
            None, alter state
            """
            self.sm.inactivity_timer.stop()
            if self.sm.__cw__ == schc_message.header.w:
                fcn = schc_message.header.fcn.fcn
                tiles_received = schc_message.payload.size // self.sm.protocol.TILE_SIZE
                tiles = schc_message.payload.as_bytes()
                for tile in range(tiles_received):
                    self._logger_.debug("Window received: {}\tTile {}".format(
                        schc_message.header.w.w, fcn))
                    self.sm.add_tile(Tile(
                        tiles[0:self.sm.protocol.TILE_SIZE // 8]
                    ), w=self.sm.__cw__, fcn=fcn)
                    tiles = tiles[self.sm.protocol.TILE_SIZE // 8:]
                    self.sm.bitmaps[self.sm.__cw__].tile_received(fcn)
                    try:
                        fcn = self.sm.bitmaps[self.sm.__cw__].get_missing(fcn=True, after=fcn)
                    except ValueError:
                        try:
                            fcn = self.sm.bitmaps[self.sm.__cw__].get_missing(fcn=True)
                        except ValueError:
                            ack = SCHCAck(
                                rule_id=self.sm.__rule_id__,
                                protocol=self.sm.protocol.id,
                                c=False,
                                dtag=self.sm.__dtag__,
                                w=self.sm.__cw__,
                                compressed_bitmap=self.sm.bitmaps[self.sm.__cw__].generate_compress()
                            )
                            ack.add_padding()
                            self.sm.message_to_send.append(ack)
                            self.sm.state = self.sm.states["waiting_phase"]
                            self.sm.state.enter_state()
                            self.sm.inactivity_timer.reset()
                            return
                self._logger_.debug("Current bitmap: {}. Waiting for w={} fcn={} tile".format(
                    self.sm.bitmaps[
                        self.sm.__cw__
                    ], self.sm.__cw__, fcn)
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
            self.sm.state = self.sm.states["receiving_phase"]
            self.sm.state.enter_state()
            self.sm.state.receive_all1_schc_fragment(schc_message)
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
                ack = SCHCAck(
                    rule_id=self.sm.__rule_id__,
                    protocol=self.sm.protocol.id,
                    c=False,
                    w=w,
                    compressed_bitmap=self.sm.bitmaps[w].generate_compress()
                )
                ack.add_padding()
                self.sm.message_to_send.append(ack)
            else:
                pass
            return

    def __init__(self, protocol, dtag=None, on_success=None):
        super().__init__(protocol, dtag=dtag)
        self.states["receiving_phase"] = AckOnErrorReceiver.ReceivingPhase(self)
        self.states["waiting_phase"] = AckOnErrorReceiver.WaitingPhase(self)
        self.states["receiving_missing_phase"] = AckOnErrorReceiver.ReceivingMissingPhase(self)
        self.state = self.states["receiving_phase"]
        self.inactivity_timer.reset()
        self.state.enter_state()
        self.on_success = on_success
        return


def std_on_expiration_time(state, alarm):
    """
    Standard expiration time (for both phases)

    Parameters
    ----------
    state : SCHCReceiver.ReceiverState
        State which Inactivity timer expired
    alarm : Timer
       Timer of machine that activates the alarm

    Returns
    -------
    None
    """
    state.sm.state = state.sm.states["error"]
    state.sm.state.enter_state()
    abort = SCHCReceiverAbort(
        rule_id=state.sm.__rule_id__,
        protocol=state.sm.protocol.id,
        dtag=state.sm.__dtag__,
        w=state.sm.__cw__
    )
    abort.add_padding()
    state.sm.message_to_send.append(abort)
    return
