"""schc_payload: SCHC Payload Class"""

from schc_base import SCHCObject


class SCHCPayload(SCHCObject):
    """
    SCHC Payload Class

    Attributes
    ----------
    content : str
        Content of payload
    """

    def __init__(self):
        super().__init__()
        self.content = ''

    def as_bits(self):
        """
        Represent the SCHCObject content in a string
        representing bit by bit

        Returns
        -------
        str :
            Bit sequence as a string
        """
        return self.content

    def as_bytes(self):
        """
        Represent payload as bytes

        Returns
        -------
        bytes:
            Payload as bytes
        """
        return SCHCObject.bits_2_bytes(self.content)

    def add_content(self, to_add):
        """
        Add content to payload

        Parameters
        ----------
        to_add : str or bytes
            An encoded content or bit sequence

        Returns
        -------
        int :
            Size of current SCHC Payload
        """
        if isinstance(to_add, str):
            self.content += to_add
            self.size = len(self.content)
        elif isinstance(to_add, bytes):
            self.content += self.bytes_2_bits(to_add)
            self.size = len(self.content) * 8
        return self.size
