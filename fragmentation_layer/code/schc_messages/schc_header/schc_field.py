""" schc_field: SCHC Field Abstract Class"""

from schc_base import SCHCObject


class SCHCField(SCHCObject):
    """
    SCHC Field Class
    """
    def __init__(self):
        super().__init__()

    def as_bytes(self):
        """
        Not to be used

        Returns
        -------
        bytes:
            b''
        """
        return b''

    def as_bits(self):
        """
        Represent the field as bits, depending on field

        Returns
        -------
        str :
            A string of bits
        """
        pass

    def format_text(self):
        """
        Gets format text for header, name and content

        Returns
        -------
        str :
            Size message
        str :
            Name of field
        str :
            Content
        """
        return "", "", ""
