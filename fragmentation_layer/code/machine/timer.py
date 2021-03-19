""" Timer: Equivalent to Timer class (PyCom) """

import threading
from typing import Callable, Tuple


class Timer:
    """
    Class implementing desire functionalities of PyCom Timer Class (
    https://docs.pycom.io/firmwareapi/pycom/machine/timer/
    ). Used for testing on local only,
    """

    class Alarm:
        """
        Used to get interrupted after a specific interval (PyCom)
        """

        def __init__(self, handler: Callable, s: float = None,
                     *, ms: int = None, us: int = None, arg: Tuple[object, ...] = None,
                     periodic: bool = False) -> None:
            if s is None and ms is None and us is None:
                raise TypeError("__init__() missing 1 required keyword only argument: 's', 'ms' or 'us'")
            self.__timer__ = None
            self.__seconds__ = sum([
                (s if s is not None else 0),
                (ms / 1e3 if ms is not None else 0),
                (us / 1e6 if us is not None else 0)
            ])
            self.__handler__ = handler
            self.__args__ = arg
            self.__periodic__ = periodic
            self.__set_alarm__()
            return

        def __set_alarm__(self) -> None:
            if self.__handler__ is None:
                return
            else:
                self.__timer__ = threading.Timer(self.__seconds__, self.__run__)
                self.__timer__.start()
                return

        def __run__(self) -> None:
            if self.__args__ is not None:
                self.__handler__(self, *self.__args__)
            else:
                self.__handler__(self)
            if self.__periodic__:
                self.__set_alarm__()
            return

        def callback(self, handler: Callable, arg: Tuple[object, ...] = None) -> None:
            """
            Specify a callback handler for the alarm.

            Parameters
            ----------
            handler : Callable
                Callback handler. If set to None, the alarm will be disabled.
            arg : Tuple, optional
                 Argument passed to the callback handler function.
                 If None is specified, the function will receive the object that triggered the alarm.

            Returns
            -------
            None
            """
            self.__handler__ = handler
            self.__args__ = arg
            self.__set_alarm__()
            return

        def cancel(self) -> None:
            """
            Disables the alarm.

            Returns
            -------
            None
            """
            if self.__timer__ is not None:
                self.__timer__.cancel()
                self.__periodic__ = False
            return
