""" schc_sender: Ack-Always Mode Sender Finite State Machine """

from __future__ import annotations
from typing import List
from schc_base import Tile
from schc_messages import SCHCReceiverAbort, SCHCAck, SCHCMessage
from schc_messages import RegularSCHCFragment, All1SCHCFragment, SCHCSenderAbort
from schc_modes import SCHCSender
from schc_parsers import SCHCParser
from schc_protocols import SCHCProtocol


class AckAlwaysModeSCHCSender(SCHCSender):
    """
    SCHC Sender Finite State Machine for Ack-Always Mode

    Attributes
    ----------
    state
    protocol
    init_state
    sending_state
    waiting_state
    lsb_window : int
        Last significant bit of current window
    tiles : List[Tile]
        List of Tile for current window
    """
    class BlindTransmission(SCHCSender.InitialPhase):
        """
        Blind Transmission phase of sender
        """
        def __init__(self, state_machine: AckAlwaysModeSCHCSender) -> None:
            super().__init__(state_machine)
            self.tile = self.state_machine.protocol.WINDOW_SIZE - 1
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Send all fragment for current window

            Parameters
            ----------
            mtu : int
                MTU available as bytes

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            if len(self.state_machine.remaining_packet) == 0 or self.tile < 0:
                raise RuntimeError("No more SCHC message to send")
            go_on = True
            message = RegularSCHCFragment(self.state_machine.__rule_id__, self.tile,
                                          protocol=self.state_machine.protocol.id,
                                          dtag=self.state_machine.__dtag__,
                                          w=self.state_machine.lsb_window)
            current_size = message.size
            available_size = mtu * 8 - current_size
            tile = Tile(self.state_machine.remaining_packet[0:available_size])
            self.state_machine.remaining_packet = self.state_machine.remaining_packet[available_size:]
            self.state_machine.tiles.append(tile)
            message.add_tile(tile)
            self.tile -= 1
            if len(self.state_machine.remaining_packet) == 0:
                message = All1SCHCFragment(rule_id=self.state_machine.__rule_id__,
                                           protocol=self.state_machine.protocol.id,
                                           dtag=self.state_machine.__dtag__,
                                           w=self.state_machine.lsb_window,
                                           rcs=self.state_machine.rcs)
                message.add_tile(tile)
                message.add_padding()
                self.state_machine.last_window = True
                self.state_machine.state = self.state_machine.sending_state
                go_on = False
            if self.tile < 0:
                self.state_machine.state = self.state_machine.waiting_state
                go_on = False
            if not go_on:
                self.state_machine.attempts.reset()
                self.state_machine.retransmission_timer.reset()
            return [message]

        def receive_message(self, message: bytes) -> SCHCMessage:
            """
            Not available on this state

            Raises
            ------
            RuntimeError
                This should not be reach on this state
            """
            raise RuntimeError("On Blind Transmission it cannot receive message")

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            """
            Not available on this state

            Raises
            ------
            RuntimeError
                This should not be reach on this state
            """
            raise RuntimeError("On Blind Transmission it cannot receive message")

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            """
            Not available on this state

            Raises
            ------
            RuntimeError
                This should not be reach on this state
            """
            raise RuntimeError("On Blind Transmission it cannot receive message")

    class RetransmissionPhase(SCHCSender.SendingPhase):
        """
        Retransmission Phase of sender

        Attributes
        ----------
        failed_ones : List[int]
            Indexes of failed tiles as are saved on state_machine.tiles
        """
        def __init__(self, state_machine: AckAlwaysModeSCHCSender) -> None:
            super().__init__(state_machine)
            self.failed_ones = list()
            return

        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Send all fragment failed on current window

            Parameters
            ----------
            mtu : int
                MTU available as bytes

            Returns
            -------
            SCHCMessage :
                SCHC Message to send
            """
            if len(self.failed_ones) == 0:
                self.state_machine.attempts.increment()
                self.state_machine.retransmission_timer.reset()
                raise RuntimeError("No more SCHC message to send")
            else:
                missing_tile = self.failed_ones.pop(0)
                fcn = self.state_machine.protocol.WINDOW_SIZE - 1 - missing_tile
                message = RegularSCHCFragment(self.state_machine.__rule_id__, fcn,
                                              protocol=self.state_machine.protocol.id,
                                              dtag=self.state_machine.__dtag__,
                                              w=self.state_machine.lsb_window)
                message.add_tile(self.state_machine.tiles[missing_tile])
            return [message]

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            if schc_message.header.c:
                self.state_machine.retransmission_timer.stop()
                self.state_machine.__current_window__ += 1
                self.state_machine.state = self.state_machine.init_state
            else:
                for i, success in enumerate(schc_message.header.compressed_bitmap.bitmap):
                    if not success:
                        self.failed_ones.append(i)
                return self.generate_message(0)

        def receive_schc_receiver_abort(self, schc_message: SCHCReceiverAbort) -> SCHCMessage:
            raise ConnectionAbortedError("Receiver send a signal to abort sending")

    class LastRetransmissionPhase(RetransmissionPhase, SCHCSender.WaitingPhase):
        """
        Retransmission Phase of last window of sender
        """
        def generate_message(self, mtu: int) -> SCHCMessage:
            """
            Send all fragment failed on last window

            Parameters
            ----------
            mtu : int
                MTU available as bytes

            Returns
            -------
            SCHCMessage:
                SCHC Message to send
            """
            if len(self.failed_ones) != 0:
                missing_tile = self.failed_ones.pop(0)
                if missing_tile == len(self.state_machine.tiles) - 1:
                    message = All1SCHCFragment(rule_id=self.state_machine.__rule_id__,
                                               protocol=self.state_machine.protocol.id,
                                               dtag=self.state_machine.__dtag__,
                                               w=self.state_machine.lsb_window,
                                               rcs=self.state_machine.rcs)
                    message.add_tile(self.state_machine.tiles[missing_tile])
                    message.add_padding()
                    return [message]
            return super().generate_message(mtu)

        def receive_schc_ack(self, schc_message: SCHCAck) -> SCHCMessage:
            if schc_message.header.c:
                raise SystemExit("Sender and Receiver check successfully")
            else:
                if len(schc_message.header.compressed_bitmap) == sum(schc_message.header.compressed_bitmap):
                    return [SCHCSenderAbort(self.state_machine.__rule_id__,
                                            self.state_machine.protocol.id,
                                            dtag=self.state_machine.__dtag__,
                                            w=self.state_machine.lsb_window)]
                else:
                    return super().receive_schc_ack(schc_message)

    def __init__(self, protocol: SCHCProtocol, rule_id: int, payload: bytes, residue: str = "", dtag: int = None) -> None:
        super().__init__(protocol, rule_id, payload, residue=residue, dtag=dtag)
        self.init_state = AckAlwaysModeSCHCSender.BlindTransmission(self)
        self.sending_state = AckAlwaysModeSCHCSender.RetransmissionPhase(self)
        self.waiting_state = AckAlwaysModeSCHCSender.LastRetransmissionPhase(self)
        self.state = self.init_state
        if protocol.M != 1:
            protocol.M = 1
        self.retransmission_timer.stop()
        self.lsb_window = int("{:0b}".format(self.__current_window__)[-1])
        self.tiles = list()
        return

    def receive_message(self, message: bytes) -> SCHCMessage:
        schc_message = SCHCParser.from_bytes(self.protocol, message)
        if schc_message.header.w == self.lsb_window:
            return super().receive_message(message)
