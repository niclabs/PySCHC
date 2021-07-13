""" schc_handler: SCHC Handler (Super) Class """

from schc_base import SCHCObject
from schc_protocols import SCHCProtocol, get_protocol


# TODO: 
class SCHCHandler:
    """
    SCHC Handler super class
    Define functions and interface of Node and Gateway concrete class

    Attributes
    ----------
    __protocol__ : SCHCProtocol
        Protocol to be use
    __sessions__ : Dict[int, Dict[int, SCHCFiniteStateMachine]]
        A dictionary with rule_id and DTag assigned to a SCGHCFiniteStateMachine
    __mtu__ : int
        MTU to use

    See Also
    --------
    SCHCFiniteStateMachine
    """
    def __init__(self, protocol, mtu):
        """
        Constructor

        Parameters
        ----------
        protocol : int
            Number indicating SCHCProtocol to use
        mtu : int
            MTU to use

        See Also
        --------
        SCHCProtocol
        """
        self.__protocol__ = get_protocol(protocol)
        self.__sessions__ = dict()
        self.__mtu__ = mtu

    def identify_session_from_message(self, message, f_port=None):
        """
        Identifies the session to use according to protocol and message

        Parameters
        ----------
        message : bytes
            A bytes message
        f_port : int, optional
            In case of using LoRaWAN, rule id to use

        Returns
        -------
        Tuple[int, int]
            Rule id and Dtag that are going to be use to find
            session (and SCHCFiniteStateMachine associated)
        """
        if self.__protocol__.id == SCHCProtocol.LoRaWAN:
            rule_id = f_port
        else:
            raise NotImplementedError("Just LoRaWAN implemented")
        protocol = get_protocol(self.__protocol__.id)
        protocol.set_rule_id(rule_id)
        dtag = SCHCObject.bytes_2_bits(message)[:protocol.T]
        if len(dtag) == 0:
            dtag = None
        else:
            dtag = int(dtag, 2)
        return rule_id, dtag

    def send_package(self, packet):
        """
        To be implemented by concrete class
        Load package to send

        Parameters
        ----------
        packet : bytes
            Packet to be fragmented

        Returns
        -------
        None
        """
        return

    def receive(self, rule_id, dtag, message):
        """
        To be implemented by concrete class
        Defines behaviour after receiving a message

        Parameters
        ----------
        rule_id : int
            Rule id of received message
        dtag : int or None
            DTag of received message
        message : bytes
            Message receive

        Returns
        -------
        None
        """
        return

    def assign_session(self, rule_id, dtag, machine):
        """
        Assigns a SCHCFiniteStateMachine (machine) to the corresponding
        rule id and dtag

        Parameters
        ----------
        rule_id : int
            Rule id defining mode
        dtag : int
            DTag to differentiates parallel packets
        machine : SCHCFiniteStateMachine
            Finite State Machine defining behaviour of fragmentation

        Returns
        -------
        None, alter self.__session__
        """
        if rule_id not in self.__sessions__.keys():
            self.__sessions__[rule_id] = dict()
        if dtag not in self.__sessions__[rule_id].keys() or self.__sessions__[rule_id][dtag].is_active() == False:
            self.__sessions__[rule_id][dtag] = machine
