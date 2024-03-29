"""schc_object: SCHC object abstract class (works as an Interface)"""


class SCHCObject:
    """
    SCHC Object Interface, implemented as an Abstract Base Class

    Attributes
    ----------
    size : int
        Size used in bits

    Notes
    -----
    bits_2_bytes and bytes_2_bits are not complement methods:
    bits_2_bytes(bytes_2_bits(some_content)) not necessarily returns some_content, and
    bytes_2_bits(bits_2_bytes(some_content)) not necessarily returns some_content
    """
    def __init__(self):
        """
        Default constructor
        """
        self.size = 0
        return

    def as_bits(self):
        """
        Represent the SCHCObject content in a string
        representing bit by bit

        Returns
        -------
        str :
            Bit sequence as a string
        """
        return ''

    def as_bytes(self):
        """
        Represent the SCHCObject content as bytes

        Returns
        -------
        bytes :
            Content in bytes
        """
        return b''

    @staticmethod
    def bytes_2_bits(content: bytes):
        """
        Turns bytes content in a text representation bit by bit

        Parameters
        ----------
        content : bytes
            Content in bytes

        Returns
        -------
        str :
            Bit sequence as a string
        """
        direct = "{:0b}".format(int.from_bytes(content, "big"))
        zeros_missing = (len(content) * 8) - len(direct)
        if zeros_missing > 0:
            return ("0" * zeros_missing) + direct
        return direct

    @staticmethod
    def bits_2_bytes(content: str):
        """
        Turns text representation bit by bit in a bytes value

        Parameters
        ----------
        content : str
            Bit sequence as a string

        Returns
        -------
        str :
            Content in bytes
        """
        byte = 0
        list_bytes = list()
        for i, bit in enumerate(content):
            byte = (byte << 1) | int(bit)
            if (i + 1) % 8 == 0:
                list_bytes.append(byte)
                byte = 0
        if len(content) % 8 != 0:
            list_bytes.append(byte)
        return bytes(list_bytes)

    @staticmethod
    def zfill(bits, length):
        """
        Completes with zeroes to the left to match length

        Parameters
        ----------
        bits : str
            Bit sequence as string
        length : int
            Wanted length, if length <= len(bits) nothing is done
        Returns
        -------
        str :
            Sequence of len = length
        """
        zeroes = length - len(bits)
        if zeroes <= 0:
            return bits
        else:
            return "{}{}".format("0" * zeroes, bits)
