""" schc_messages: SCHCMessage class """

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Tuple
from schc_base import SCHCObject, SCHCProtocol
from schc_messages import SCHCHeader, SCHCPayload, SCHCPadding


class SCHCMessage(SCHCObject, ABC):
    """
    SCHCMessage abstract class

    +-----------------+------------------+---------------------+
    | Fragment Header | Fragment Payload | passing (as needed) |
    +-----------------+------------------+---------------------+

    Attributes
    ----------
    header : SCHCHeader
        Header, contains at least Rule ID and protocol specified when needed
    payload : SCHCPayload
        Payload of message
    padding : SCHCPadding
        Padding when needed
    protocol : SCHCProtocol
        Protocol, specified in case it is needed, default SCHCProtocol.LoRaWAN
    size
    """

    def __init__(self, rule_id: int, protocol: int = 1, **kwargs) -> None:
        """
        Initialize message

        Parameters
        ----------
        rule_id : int
            RuleId field
        protocol : int, optional
            Protocol to use, default LoRaWAN

        Other Parameters
        ----------------
        Parameters of SCHCHeader

        See Also
        --------
        schc_message.schc_header.schc_header.SCHCHeader :
            Description of Other Parameters
        """
        super().__init__()
        self.header = SCHCHeader(rule_id, protocol=protocol, **kwargs)
        self.payload = SCHCPayload()
        self.padding = SCHCPadding()
        self.protocol = SCHCProtocol(protocol, rule_id=rule_id)
        self.size = sum([
            self.header.size,
            self.payload.size,
            self.padding.size
        ])

    @staticmethod
    def from_bytes(received: bytes, protocol: int = 1) -> SCHCMessage:
        """
        Generate an instance of SCHCMessage

        Parameters
        ----------
        received : bytes
            Bytes received
        protocol : int
            Protocol to use from decode received

        Returns
        -------
        SCHCMessage :
            New instance with received content
        """
        pass

    def as_bytes(self, **kwargs) -> Tuple[bytes, ...]:
        """
        Returns a tuple of bytes of the SCHCMessage

        Other Parameters
        ----------------
        kwargs :
            To be implemented for class that extends this class

        Returns
        -------
        Tuple[bytes]:
            A tuple of bytes. Generally just one element
            in LoRaWan protocol, two elements (FPort, LoRaWan payload)

        Raises
        ------
        NotImplemented
            Any other SCHC protocol, but LoRaWAN
        """
        message = self.header.as_bits() + self.payload.as_bits() + self.padding.as_bits()
        if self.protocol.id == 0:
            return self.bits_2_bytes(message),
        if self.protocol.id == SCHCProtocol.LoRaWAN:
            fport = message[0:self.protocol.FPORT_LENGTH]
            lorawan_payload = message[self.protocol.FPORT_LENGTH:]
            return self.bits_2_bytes(fport), self.bits_2_bytes(lorawan_payload)
        else:
            raise NotImplemented("Just LoRaWAN protocol is currently implemented")

    def add_padding(self) -> int:
        """
        Adds padding to match MTU

        Returns
        -------
        int :
            Size of message
        """
        last_word_size = self.size % self.protocol.L2_WORD
        if last_word_size == 0:
            logging.debug("No padding added")
            return 0
        pad_size = self.padding.add(self.protocol.L2_WORD - last_word_size)
        self.size = self.header.size + self.payload.size + pad_size
        return self.size

    @abstractmethod
    def as_text(self) -> str:
        """
        Writes message with specifications

        Returns
        -------
        str :
            SCHC Message as text format
        """
        header_text = "|--- SCHC Fragment Header {}---|"
        return header_text
