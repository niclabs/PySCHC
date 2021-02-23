""" timer: Timer class """
from time import time


class Timer:
    """
    Timer Abstract class

    Attributes
    ----------
    __start_time__ : float
        Seconds from 1970-01-01 at start timer
    __max_time__ : int
        Maximum time in seconds
    __running__ : bool
        If timer is running
    """
    def __init__(self, max_time: int) -> None:
        """
        Constructor

        Parameters
        ----------
        max_time : int
            Maximum time in seconds
        """
        self.__start_time__ = time()
        self.__max_time__ = max_time
        self.__running__ = True
        return

    def reset(self) -> None:
        """
        Resets timer

        Returns
        -------
        None, alter self
        """
        self.__start_time__ = time()
        self.__running__ = True
        return

    def stop(self) -> None:
        """
        Stops timer

        Returns
        -------
        None, alter self
        """
        self.__running__ = False
        return

    def expired(self) -> bool:
        """
        Whether or not timer expires

        Returns
        -------
        bool :
            True if timer has expired
        """
        if self.__running__:
            return time() - self.__start_time__ >= self.__max_time__
        else:
            return False
