""" sigfox: Sigfox parser function """


def parse(message):
    """
    Parses message receive according to Sigfox Profile

    Parameters
    ----------
    message : bytes
        Bytes received

    Returns
    -------
    SCHCMessage :
        SCHCMessage with attributes given by content received

    Raises
    ------
    NotImplemented
        Protocol not available to parser
    """
    raise NotImplementedError("Sigfox not implemented")
