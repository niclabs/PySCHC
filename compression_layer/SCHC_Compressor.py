import struct
import binascii

from SCHC_Parser import SCHC_Parser
from SCHC_RuleManager import SCHC_RuleManager


class SCHC_Compressor:

    def __init__(self, rm):
        self.rule_manager = rm
        self.context = rm.context
        self.parser = SCHC_Parser()
        self.CompressionActions = {
            "not-sent": self.ca_not_sent,
            "value-sent": self.ca_value_sent,
            "mapping-sent": self.ca_mapping_sent,
            "LSB": self.ca_lsb,
            "devIID": self.ca_send_nothing,
            "appIID": self.ca_app_iid,
            "compute-length": self.ca_send_nothing,
            "compute-checksum": self.ca_send_nothing
        }

    def ca_not_sent(self, length, tv, fv, mo):
        if mo is "equal":
            return None
        else:
            print("Warning: The CDA \"not-send\" SHOULD be used with the \"equal\" MO")
            return None

    def ca_value_sent(self, length, tv, fv, mo):
        if mo != "ignore":
            print("Warning: The CDA \"value-sent\" SHOULD be used with the \"ignore\" MO")
        return self.__left_align_bits(length, fv[0])

    def ca_mapping_sent(self, length, tv, fv, mo):
        max_index = -1
        mapping = None
        if type(tv) is dict:
            for mappingID, mappingValue in tv.items():
                if mappingValue == fv[0]:
                    mapping = mappingID
                if mappingID > max_index:
                    max_index = mappingID
        elif type(tv) is list:
            max_index = len(tv) - 1
            for i in range(len(tv)):
                if tv[i] == fv[0]:
                    mapping = i
                    break
        
        length_remain = 0
        while max_index > 0:
            length_remain += 1
            max_index >>= 1

        return self.__left_align_bits(length_remain, mapping)

    def ca_lsb(self, length, tv, fv, mo):
        length_remain = length - int(mo[4:-1]) # length - n_bits
        val = fv[0] - (tv << length_remain)
        return self.__left_align_bits(length_remain, val)

    def ca_send_nothing(self, length, tv, fv, mo): # used for deviid and compute-*. doesnt show warning
        return None
    
    def ca_app_iid(self, length, tv, fv, mo):
        raise NotImplementedError

    def __left_align_bits(self, length, value):
        length_cociente = length // 8
        length_remain = length % 8
        mask = 0xFF
        buff = bytearray(length_cociente + (1 if length_remain else 0))
        
        # full bytes
        for i in range(length_cociente):
            struct.pack_into(">B", buff, i, (value >> (length_remain + (length_cociente - i - 1) * 8)) & mask)

        # remaining bits
        if length_remain != 0:
            struct.pack_into(">B", buff, length_cociente, (value << (8 - length_remain)) & mask)

        return bytes(buff), length

    def compress(self, package, direction):
        # Parsing Package
        self.parser.parser(package, direction)

        # Get Rule ID
        rule_id = self.rule_manager.find_rule_from_headers(self.parser.header_fields, direction)
        rule_id_bf = struct.pack(">B", rule_id)
        if rule_id == SCHC_RuleManager.RULE_ID_NOT_COMPRESSED:
            packet = b''.join([rule_id_bf, bytes(self.parser.unparsed_headers), bytes(self.parser.udp_data[0])])
            unused_bits = 0

        else:
            # Get Compression Residue
            comp_res_bf, bit_pos = self.calc_compression_residue(self.parser.header_fields, self.rule_manager.get_rule_from_id(rule_id), direction)

            # Shift payload bytes
            almost_packet = self.add_bits_to_array(comp_res_bf, bit_pos, self.parser.udp_data[0])

            packet = b''.join([rule_id_bf, bytes(almost_packet)])
            unused_bits = 8 - (bit_pos % 8)

            print("Length of uncompressed headers: " + str(len(self.parser.unparsed_headers)) + " bytes")
            print("Length of compressed headers: " + str((bit_pos + 7) // 8) + " bytes")
            hc_len = (bit_pos + 7) // 8
            pkg_len = len(self.parser.unparsed_headers)
            temp = (pkg_len - hc_len) * 100 / pkg_len
            print('Compression: %.2f%%' % temp)

        return packet, unused_bits


    def add_bits_to_array(self, array, offset, value):
        mask = 0xFF
        if offset % 8 == 0:
            for byte in value:
                array.append(byte)
        else:
            for byte in value:
                array[-1] += byte >> (offset % 8)
                array.append((byte << (8 - offset % 8)) & mask)
        return array

    def calc_compression_residue(self, headers, rule, direction):
        buffer = []
        offset = 0
        for fd in rule["content"]:
            for header in headers:
                if header[0] == fd[0] and (direction == fd[3] or fd[3] == 'Bi'):
                    fv = headers[header]
                    length = fd[1]
                    tv = fd[4]
                    mo = fd[5]
                    cda = fd[6]
                    result = self.CompressionActions.get(cda)(length, tv, fv, mo)
                    if result is not None:
                        residue, res_length = result
                        buffer = self.add_bits_to_array(buffer, offset, residue)
                        offset += res_length
                        # ceiling(offset / 8)
                        if len(buffer) > ((offset + 7) // 8):
                            buffer.pop()
        return buffer, offset
