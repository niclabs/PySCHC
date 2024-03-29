"""dtag: Datagram Tag Class"""

from schc_messages.schc_header import SCHCField


class DTag(SCHCField):
    """
    Datagram Tag Class

    Attributes
    ----------
    dtag : int
        DTag value as an integer for simplification
    t : int
        Size of Dtag in bits (given according to rule_id)
    """

    def __init__(self, dtag, t):
        """
        DTag constructor

        Parameters
        ----------
        dtag : int
            DTag value as an integer for simplification
        t : int
            Size of Dtag in bits (given according to rule_id)
        """
        super().__init__()
        self.dtag = dtag
        self.t = t
        self.size = self.t
        return

    def as_bits(self):
        """
        Returns the bits representation of the SCHC Header

        Returns
        -------
        str :
            Bit representation
        """
        if self.t == 0:
            return ""
        else:
            return self.zfill("{:0b}".format(self.dtag), self.t)

    def format_text(self):
        """
        Gets format text to write message as text

        Returns
        -------
        str :
            Size of DTag, as T = {}
        str :
            Name of field: DTag
        content :
            Content in bits
        """
        if self.t != 0:
            text_size = " T={} ".format(self.t)
            if len(text_size) < 6:
                text_size += " "
            content = self.as_bits()
            if len(content) < len(text_size):
                content += " " * (len(text_size) - len(content))
                tag = " DTag "
            else:
                text_size += " " * (len(content) - len(text_size))
                tag = " DTag " + " " * (len(text_size) - 6)
            return text_size, tag, content
        else:
            return super().format_text()
