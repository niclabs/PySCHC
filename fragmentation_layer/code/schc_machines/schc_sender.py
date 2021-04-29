""" schc_sender: SCHC Finite State Machine Sender Behaviour """

from schc_base import SCHCTimer, SCHCObject
from schc_machines import SCHCFiniteStateMachine
from schc_messages import SCHCAck, SCHCReceiverAbort
from schc_parsers import SCHCParser


class SCHCSender(SCHCFiniteStateMachine):
    """
    SCHC Finite State Machine for Receiver behaviour

    Attributes
    ----------
    protocol
    retransmission_timer : Timer
        Retransmission Timer to abort retransmitting SCHC Messages
    packet : bytes
        Packet to send
    residue : str
        Compression residue (as bits)
    remaining_packet : str
        Rest of packet to send encoding as 0 and 1 string
    """
    __type__ = "Sender"

    class SenderState(SCHCFiniteStateMachine.State):
        """
        Sender State
        """
        def receive_message(self, message: bytes):
            """
            Does something when receiving bytes

            Parameters
            ----------
            message : bytes
                A message as bytes

            Returns
            -------
            None, alter state

            Raises
            ------
            ValueError
                In case bytes received could not be decoded to a SCHC Message
            """
            schc_message = SCHCParser.from_bytes(self.sm.protocol, message)
            if isinstance(schc_message, SCHCAck):
                return self.receive_schc_ack(schc_message)
            elif isinstance(schc_message, SCHCReceiverAbort):
                return self.receive_schc_receiver_abort(schc_message)
            else:
                raise ValueError("Bytes received could not be decoded")

        def receive_schc_ack(self, schc_message):
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCAck
                Message received

            Returns
            -------
            None, alter state

            Raises
            ------
            RuntimeError
                Behaviour unreachable
            """
            raise RuntimeError("Behaviour unreachable")

        def receive_schc_receiver_abort(self, schc_message):
            """
            Does something when SCHC Message

            Parameters
            ----------
            schc_message : SCHCReceiverAbort
                Message received

            Returns
            -------
            None, alter state
            """
            self.sm.state = self.sm.states["error"]
            self.sm.state.enter_state()
            return

    def __init__(self, protocol, payload, padding=0, dtag=None):
        """
        Constructor

        Parameters
        ----------
        protocol
        payload : bytes
            Payload to fragment
        padding : int
            Padding size
        dtag
        """
        super().__init__(protocol, dtag=dtag)
        self.retransmission_timer = SCHCTimer(self.on_expiration_time, protocol.RETRANSMISSION_TIMER)
        self.retransmission_timer.stop()
        self.packet = payload
        if padding == 0:
            self.remaining_packet = SCHCObject.bytes_2_bits(payload)
            self.rcs = self.protocol.calculate_rcs(self.remaining_packet)
        else:
            payload_as_bits = SCHCObject.bytes_2_bits(payload)
            self.remaining_packet = payload_as_bits[0:-padding]
            self.rcs = self.protocol.calculate_rcs(payload_as_bits)
        self.__end_msg__ = "Message sent and acknowledged"
        return
