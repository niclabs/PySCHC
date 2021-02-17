""" schc_messages: SCHCMessage class """

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Tuple
from schc_base import SCHCObject
from schc_protocols import get_protocol, SCHCProtocol
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
        self.protocol = get_protocol(protocol, rule_id=rule_id)
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

    def as_bytes(self) -> Tuple[bytes, ...]:
        """
        Returns a tuple of bytes of the SCHCMessage

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
        Adds padding to match L2 word size

        Returns
        -------
        int :
            Size of message
        """
        last_word_size = self.size % self.protocol.L2_WORD
        if last_word_size == 0:
            logging.debug("No padding added")
            return self.size
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
        pass

    def base_as_text(self, header_text: str) -> str:
        """
        Base to use for all message to simplify implementation
        of as_text() method

        Parameters
        ----------
        header_text : str
            Text to show on the header. Title of the message

        Returns
        -------
        str :
            SCHC Message as text format
        """
        second_header = " " * (max(len(self.header.rule_id.as_bits()), 8) + 1) + "|"
        text_tags = "| RuleID "
        content_text = "|{}".format(self.header.rule_id.as_bits())
        if len(content_text) >= len(text_tags):
            text_tags += " " * (len(content_text) - len(text_tags)) + "|"
            content_text += "|"
        else:
            text_tags += "|"
            content_text += " " * (len(text_tags) - len(content_text)) + "|"
        fields = [
            self.header.dtag,
            self.header.w,
            self.header.fcn,
            self.header.rcs,
            self.header.c,
        ]
        for field in fields:
            if field.size != 0:
                text_size, tag, content = field.format_text()
                second_header += text_size + "|"
                text_tags += tag + "|"
                content_text += content + "|"
        header_length = len(header_text) - 3
        if len(second_header) > header_length:
            header_text = header_text.format(" " * (len(second_header) - header_length))
        else:
            header_text = header_text.format("")
        if self.header.compressed_bitmap.size != 0:
            _, tag, bitmap = self.header.compressed_bitmap.format_text()
            text_tags += tag + "|"
            content_text += bitmap + "|"
        if self.payload.size != 0:
            if self.payload.size >= 18:
                text_tags += " Fragment Payload " + " " * (self.payload.size - 18) + "|"
                content_text += self.payload.as_bits() + "|"
            else:
                text_tags += " Fragment Payload " + "|"
                content_text += self.payload.as_bits() + " " * (18 - self.payload.size) + "|"
        if self.padding.size != 0:
            if self.padding.size >= 9:
                text_tags += " padding " + " " * (self.padding.size - 9) + "|"
                content_text += self.padding.as_bits() + "|"
            else:
                text_tags += " padding " + "|"
                content_text += self.padding.as_bits() + " " * (9 - self.padding.size) + "|"
        return "{}{}\n{}\n{}".format(header_text, second_header,
                                     text_tags, content_text)
