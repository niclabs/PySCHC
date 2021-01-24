""" schc_field: SCHC Field Abstract Class"""

from abc import ABC, abstractmethod
from typing import Tuple

from schc_base import SCHCObject


class SCHCField(SCHCObject, ABC):
    """
    SCHC Field Class
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def as_bits(self) -> str:
        """
        Represent the field as bits, depending on field

        Returns
        -------
        str :
            A string of bits
        """
        pass

    def format_text(self) -> Tuple[str, str, str]:
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
