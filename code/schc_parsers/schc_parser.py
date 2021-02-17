""" schc_parser: SCHCParser class that generate message from bytes """

from schc_protocols import SCHCProtocol
from schc_messages import SCHCMessage, SCHCAck


class SCHCParser:
    """
    SCHC Parser Class
    """

    @staticmethod
    def from_bytes(protocol: SCHCProtocol, message: bytes) -> SCHCMessage:
        """
        Generates SCHC Message from bytes received

        Parameters
        ----------
        protocol : SCHCProtocol
            Protocol to use and parser bytes
        message : bytes
            Message received

        Returns
        -------
        SCHCMessage :
            Message with SCHC Format

        Raises
        ------
        NotImplemented
            Protocol not available to parser
        """
        if protocol.id == SCHCProtocol.LoRaWAN:
            from schc_parsers.lo_ra_wan import parse
        elif protocol.id == SCHCProtocol.Sigfox:
            from schc_parsers.sigfox import parse
        else:
            raise NotImplementedError("Protocol not available to parse")
        return parse(message)


if __name__ == '__main__':
    from schc_protocols import LoRaWAN
    SCHCParser.from_bytes(LoRaWAN(), b'\x14\xd1Hello')
    from schc_protocols import Sigfox
    protocol = Sigfox()
    SCHCParser.from_bytes(protocol, b'\x14\xd1Hello')
