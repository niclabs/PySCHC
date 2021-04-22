""" ack_always_receiver: AckAlways receiver state machine """

from typing import List
from schc_machines import SCHCReceiver, AckAlways
from schc_messages import SCHCMessage, RegularSCHCFragment, SCHCAck, All1SCHCFragment
from schc_protocols import SCHCProtocol


class AckAlwaysReceiver(AckAlways, SCHCReceiver):
    """
    AckAlways Receiver State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    """
    class ReceivingPhase(SCHCReceiver.ReceiverState):
        """
        Receiving Phase of Ack Always
        """
        __name__ = "Receiving phase"

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

        def receive_regular_schc_fragment(self, schc_message):
            """
            Actions when receive a Regular SCHC Fragment

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            if self.state_machine.__current_window__ == schc_message.header.w:
                self._logger_.debug("Window received: {}\tTiles from: 0 to 0".format(
                    schc_message.header.w.w))
                self.state_machine.payload.add_content(schc_message.payload.as_bytes())
                self.state_machine.bitmap.tile_received(schc_message.header.fcn.fcn)
                ack = SCHCAck(self.state_machine.__rule_id__,
                              self.state_machine.protocol.id, c=False,
                              dtag=self.state_machine.__dtag__,
                              w=self.state_machine.__current_window__,
                              compressed_bitmap=self.state_machine.bitmap.generate_compress()
                )
                ack.add_padding()
                self.state_machine.message_to_send.append(ack)
                self.state_machine.state = self.state_machine.states["waiting_phase"]
                self.state_machine.state.enter_state()
                return
            else:
                self._logger_.debug("Different window received")
            return

        def receive_all1_schc_fragment(self, schc_message):
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
                # TODO check what happens with padding
                rcs = self.state_machine.protocol.calculate_rcs(
                    self.state_machine.payload.as_bits()
                )
                integrity = rcs == schc_message.header.rcs.rcs
                if integrity:
                    self._logger_.debug("Integrity check successful")
                    compressed_bitmap = None
                    next_state = self.state_machine.states["cleanup_phase"]
                else:
                    self._logger_.error("Integrity check failed:\tSender: {}\tReceiver:{}".format(
                        schc_message.header.rcs.rcs,
                        rcs
                    ))
                    compressed_bitmap = self.state_machine.bitmap.generate_compress()
                    next_state = self.state_machine.states["waiting_phase"]
                ack = SCHCAck(self.state_machine.__rule_id__,
                              self.state_machine.protocol.id,
                              c=integrity,
                              dtag=self.state_machine.__dtag__,
                              w=self.state_machine.__current_window__,
                              compressed_bitmap=compressed_bitmap
                )
                ack.add_padding()
                self.state_machine.message_to_send.append(ack)
                self.state_machine.state = next_state
                self.state_machine.state.enter_state()
                return
            else:
                self._logger_.debug("Different window received")
                return

        def receive_schc_ack_req(self, schc_message):
            """
            Actions when receive a SCHC Ack Request

            Parameters
            ----------
            schc_message : SCHCAckReq
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            # if w current_window:
            #   sendACK(bad)
            # else
            #   return silently

        def receive_schc_sender_abort(self, schc_message):
            """
            Actions when receive a SCHC Sender Abort

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

    class WaitingPhase(SCHCReceiver.ReceiverState):
        """
        Waiting Phase of Ack Always
        """
        __name__ = "Waiting phase"

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

        def receive_all1_schc_fragment(self, schc_message):
            """
            Actions when receive a All-1 SCHC Fragment

            Parameters
            ----------
            schc_message : All1SCHCFragment
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            # TODO if window is last window
            if schc_message.header.w != self.state_machine.__current_window__:
                self.state_machine.__current_window__ = schc_message.header.w.w
                self._logger_.debug("Starting reception of window {}".format(
                    self.state_machine.__current_window__))
                self.state_machine.bitmap = Bitmap(self.state_machine.protocol)
                self.state_machine.state = self.state_machine.states["receiving_phase"]
                self.enter_state()
                self.state_machine.state.receive_all1_schc_fragment(schc_message)
            else:
                # if not last_window: pass
                # else: TODO
                pass
            return

        def receive_schc_ack_req(self, schc_message):
            """
            Actions when receive a SCHC Ack Request

            Parameters
            ----------
            schc_message : SCHCAckReq
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            # TODO if window is last window and w != window
            # if w is current window:
            #   resend ack
            # else
            #   self.state_machine.__current_window__ += 1
            #   self.state_machine.bitmap = Bitmap(...)
            #   send ack
            #   change_state(receiving)
            
            return

        def receive_schc_sender_abort(self, schc_message):
            """
            Actions when receive a SCHC Sender Abort

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

    class CleanupPhase(SCHCReceiver.ReceiverState):
        """
        Clean-up Phase of Ack Always
        """
        __name__ = "Cleanup phase"

        def generate_message(self, mtu):
            """
            Generates SCHC Message when this method is
            called. Make sure size (access with method schc_message.size),
            in bits, is less than mtu, in bytes.
            """
            pass

        def receive_regular_schc_fragment(self, schc_message):
            """
            Actions when receive a Regular SCHC Fragment

            Parameters
            ----------
            schc_message : RegularSCHCFragment
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

        def receive_all1_schc_fragment(self, schc_message):
            """
            Actions when receive a All-1 SCHC Fragment

            Parameters
            ----------
            schc_message : All1SCHCFragment
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

        def receive_schc_ack_req(self, schc_message):
            """
            Actions when receive a SCHC Ack Request

            Parameters
            ----------
            schc_message : SCHCAckReq
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

        def receive_schc_sender_abort(self, schc_message):
            """
            Actions when receive a SCHC Sender Abort

            Parameters
            ----------
            schc_message : SCHCSenderAbort
                SCHC Message received

            Returns
            -------
            None, alter state
            """
            return

    def __init__(self, protocol, dtag = None):
        super().__init__(protocol, dtag=dtag)
        AckAlways.__init__(self)
        self.states["name_your_state"] = AckAlwaysReceiver.TemplatePhase(self)
        # self.states["other_state"] = AckAlwaysReceiver.OtherPhase(self)
        self.state = self.states["name_your_phase"]  # Initial State
        self.state.enter_state()  # This generates logs to know current states
        # Check schc_machines/schc_receiver.py and schc_machines/schc_fsm.py
        # to check other attributes of this class.
        # Anything else needed
        return
