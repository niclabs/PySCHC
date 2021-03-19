""" attempts_counter: Attempts counter class """


class AttemptsCounter:
    """
    Attempts Counter class

    Attributes
    ----------
    __max_value__ : int
        Maximum value reachable
    """
    def __init__(self, max_value: int) -> None:
        """
        Constructor

        Parameters
        ----------
        max_value : int
            Max value reachable
        """
        self.__count__ = 0
        self.__max_value__ = max_value
        return

    def reset(self) -> None:
        """
        Reset counter

        Returns
        -------
        None, alter self
        """
        self.__count__ = 0
        return

    def increment(self) -> None:
        """
        Increment counter

        Returns
        -------
        None, alter self
        """
        self.__count__ += 1
        return

    def exceeds_max(self) -> bool:
        """
        Whether or not counter reaches maximum value

        Returns
        -------
        bool :
            True if max value was reached
        """
        return self.__count__ >= self.__max_value__
