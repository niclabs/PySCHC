""" downlink_sender: Downlink sender state machine """

from schc_machines import SCHCSender, AckAlways
from schc_messages import SCHCMessage, SCHCAck, SCHCReceiverAbort
from schc_protocols import SCHCProtocol


class DownlinkSender(AckAlways, SCHCSender):
    """
    Downlink Sender State Machine with Ack-on-Error Mode

    Attributes
    ----------
    protocol
    state
    residue
    """
    class SendingPhase(SCHCSender.SenderState):
        """
        Sending Phase of Ack Always
        """
        __name__ = "Sending Phase"

        def generate_message(self, mtu):
            """
            TODO Doc
            """
            mtu_available = (mtu - (self.state_machine.regular_message_header_size // 8)) * 8
            if len(self.state_machine.remaining_packet) <= mtu_available: # last window/tile
                # if len(self.state_machine.remaining_packet) > (mtu - (self.state_machine.all1_message_header_size // 8)) * 8
                # border condition
                # else
                self.state_machine.__last_window__ = True
                new_tile = self.state_machine.remaining_packet
                self.state_machine.remaining_packet = list()
                message = All1SCHCFragment(
                    self.state_machine.__rule_id__,                       
                    self.state_machine.__fcn__,
                    self.state_machine.protocol.id,
                    self.state_machine.__dtag__,
                    self.state_machine.__current_window__
                )
            else:
                new_tile = self.state_machine.remaining_packet[:mtu_available]
                self.state_machine.remaining_packet = self.state_machine.remaining_packet[mtu_available:]
                message = RegularSCHCFragment(
                    self.state_machine.__rule_id__,
                    self.state_machine.__fcn__,
                    self.state_machine.protocol.id,
                    self.state_machine.__dtag__,
                    self.state_machine.__current_window__
                )
            message.add(new_tile)
            self.state_machine.last_message = message
            self.state_machine.state = self.state_machine.states["waiting_phase"]
            self.state_machine.state.enter_state()
            self.state_machine.retransmission_timer.reset()   
            message.add_padding()
            self._logger_.schc_message(message)
            return regular_message

    class WaitingPhase(SCHCSender.SenderState):
        """
        # TODO:
        Waiting Phase of Ack Always
        """
        __name__ = "Waiting Phase"

        def generate_message(self, mtu):
            """
            TODO Doc
            """
            raise GeneratorExit("Awaits for Ack after a windows was sent")

        def receive_schc_ack(self, schc_message: SCHCAck) -> None:
            """
            Receive an Ack after a window is fully sent

            Parameters
            ----------
            schc_message : SCHCAck
                SCHCAck reporting end of transmission or window

            Returns
            -------
            None, alter state
            """
            # TODO not specified if W is not current window
            if self.state_machine.__last_window__:
                # TODO not specified W is not last window
                if schc_message.header.c.c:
                    self.state_machine.state = self.state_machine.states["end"]
                    self.state_machine.state.enter_state()
                    return    
                else:
                    # TODO send sender-abort
                    return
            else:
                self.state_machine.bitmap = Bitmap.from_compress_bitmap(
                    schc_message.header.compressed_bitmap.bitmap, self.state_machine.protocol)
                self._logger_.debug("Received bitmap: {}".format(self.state_machine.bitmap))
                if sum(self.state_machine.bitmap) == len(self.state_machine.bitmap):
                    self.state_machine.state = self.state_machine.states["sending_phase"]
                    self.state_machine.retransmission_timer.stop()
                    self.state_machine.__current_window__ += 1
                    self.state_machine.state.enter_state()
                    return
                else:
                    # TODO: 
                    # change_state("Retransmiting")
                    return

        def receive_schc_receiver_abort(self, schc_message):
            """
            Actions when receive a SCHC Receiver Abort Message

            Parameters
            ----------
            schc_message : SCHCReceiverAbort
                Message received

            Returns
            -------
            None, alter state
            """
            return

    class RetransmitingPhase(SCHCSender.SenderState):
        """
        # TODO:
        This is a state. Change as needed and copy/paste to 
        implement other state
        """
        __name__ = "Retransmiting phase"

        def generate_message(self, mtu):
            """
            Generates SCHC Message when this method is
            called. Make sure size (access with method schc_message.size),
            in bits, is less than mtu, in bytes.
            """
            pass

    def __init__(self, protocol, payload, residue = "", dtag = None):
        super().__init__(protocol, payload, residue=residue, dtag=dtag)
        AckAlways.__init__(self)
        self.states["name_your_phase"] = DownlinkSender.TemplatePhase(self)
        # Could be harcoded... probably not a good idea
        self.regular_message_header_size = RegularSCHCFragment(
            self.state_machine.__rule_id__,
            self.state_machine.__fcn__,
            self.state_machine.protocol.id,
            self.state_machine.__dtag__,
            self.state_machine.__current_window__
        ).size
        self.all1_message_header_size = All1SCHCFragment(
            self.state_machine.__rule_id__,
            self.state_machine.__fcn__,
            self.state_machine.protocol.id,
            self.state_machine.__dtag__,
            self.state_machine.__current_window__
        ).size
        self.last_message = None
        self.state = self.states["name_your_phase"]  # Initial State
        self.state.enter_state()  # This generates logs to know current states
        # Calculates rcs, this is implemented in protocol (schc_protocols/lorawan.py)
        self.rcs = self.protocol.calculate_rcs(self.remaining_packet + padding)
        # Check schc_machines/schc_sender.py and schc_machines/schc_fsm.py
        # to check other attributes of this class.
        # Anything else needed
        return
