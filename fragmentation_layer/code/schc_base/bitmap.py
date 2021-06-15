""" bitmap: Bitmap class """


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
    def __init__(self, protocol, short_size=None):
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

    def generate_compress(self):
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

    def tile_received(self, fcn):
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

    @staticmethod
    def from_compress_bitmap(bitmap, protocol):
        """
        Calculated bitmap from bitmap of compress_bitmap on header
        of a message

        Parameters
        ----------
        bitmap : List[bool]
            bitmap attribute of compressed_bitmap of header of a SCHCMessage
        protocol : SCHCProtocol
            protocol to use

        Returns
        -------
        Bitmap :
            A Bitmap object
        """
        calculated_bitmap = Bitmap(protocol)
        calculated_bitmap.__bitmap__ = bitmap
        calculated_bitmap.__bitmap__ += [True] * (protocol.WINDOW_SIZE - len(bitmap))
        return calculated_bitmap

    def is_missing(self):
        """
        Return whether or not there are tiles missing

        Returns
        -------
        bool
            True if there are missing tiles
        """
        return len(self.__bitmap__) > sum(self.__bitmap__)

    def has_missing(self):
        """
        Whether is a missing value so far

        Returns
        -------
        bool
            True if there are missing tiles between ones
        """
        i = 0
        for i, bit in enumerate(self.__bitmap__):
            if not bit:
                break
        return 0 < sum(self.__bitmap__[i+1:])

    def get_missing(self, fcn=False):
        """
        Gets first index of reported missing tile. If fcn is True, passes
        as fcn

        Parameters
        ----------
        fcn : bool, optional
            If fcn is True, missing as fcn

        Returns
        -------
        int
            First index with missing tile
        """
        i = self.__bitmap__.index(False)
        if fcn:
            return self.protocol.WINDOW_SIZE - 1 - i
        else:
            return i

    def get_received_tiles(self):
        """
        Gets number of received tiles

        Returns
        -------
        int
            Tiles received and reported
        """
        return sum(self.__bitmap__)

    def __repr__(self):
        return "".join(["1" if i else "0" for i in self.__bitmap__])

    def __len__(self):
        return len(self.__bitmap__)

    def __iter__(self):
        for bit in self.__bitmap__:
            yield bit
