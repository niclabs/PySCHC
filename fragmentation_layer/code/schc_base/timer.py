""" timer: Timer class """

from typing import Callable
from machine import Timer


class SCHCTimer:
    """
    Timer class for retransmission and inactivity timer

    Attributes
    ----------
    __alarm__ : Timer.Alarm
        Alarm that execute on expire
    __handler__ : Callable
        Function to call on expiration
    __max_time__ : int
        Time on expiration
    """
    def __init__(self, handler: Callable, max_time: int) -> None:
        """
        Constructor

        Parameters
        ----------
        max_time : int
            Maximum time in seconds
        """
        self.__alarm__ = Timer.Alarm(handler, max_time)
        self.__handler__ = handler
        self.__max_time__ = max_time
        return

    def reset(self) -> None:
        """
        Resets timer

        Returns
        -------
        None, alter self
        """
        self.__alarm__.cancel()
        self.__alarm__ = Timer.Alarm(self.__handler__, self.__max_time__)
        return

    def stop(self) -> None:
        """
        Stops timer

        Returns
        -------
        None, alter self
        """
        self.__alarm__.cancel()
        return
