""" bitmap: Bitmap class """

from typing import List
from schc_protocols import SCHCProtocol


class Bitmap:
    """
    Bitmap class to register tiles received on windows

    Attributes
    ----------
    protocol : SCHCProtocol
        Protocol to use on Bitmap
    __bitmap__ : List
        List of bits with WINDOW_SIZE length
    """
    def __init__(self, protocol: SCHCProtocol, short_size: int = None) -> None:
        """
        Constructor

        Parameters
        ----------
        protocol : SCHCProtocol
            Protocol to use on bitmap
        short_size : int
            In case is the bitmap of the last window, number of tiles of last window
        """
        self.protocol = protocol
        if short_size is not None:
            self.__bitmap__ = [False] * short_size
        else:
            self.__bitmap__ = [False] * protocol.WINDOW_SIZE
        return

    def generate_compress(self) -> List[bool]:
        """
        Compress Bitmap of ACK Message

        Returns
        -------
        List[bool]:
            Generate Compressed Bitmap field
        """
        if len(self.__bitmap__) == 1:
            return self.__bitmap__.copy()
        else:
            header_length = sum([
                self.protocol.RULE_SIZE, self.protocol.T,
                self.protocol.M, 1
            ])
            scissor = len(self.__bitmap__)
            while self.__bitmap__[scissor - 1] and scissor > 0:
                scissor -= 1
            while (scissor + header_length) % self.protocol.L2_WORD != 0 and scissor > -1:
                scissor += 1
            return self.__bitmap__[0:scissor].copy()

    def tile_received(self, fcn: int) -> None:
        """
        Registers a tile was received

        Parameters
        ----------
        fcn : int
            Number of Tile received

        Returns
        -------
        None, alter self
        """
        self.__bitmap__[-fcn - 1] = True
        return

    def __repr__(self) -> str:
        return "".join(["1" if i else "0" for i in self.__bitmap__])
