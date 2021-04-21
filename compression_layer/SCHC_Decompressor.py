import struct
import binascii
from Crypto.Cipher import AES

from SCHC_Parser import SCHC_Parser
from SCHC_RuleManager import SCHC_RuleManager


class SCHC_Decompressor:
    def __init__(self, rm):
        self.rule_manager = rm
        self.context = rm.context
        self.parser = SCHC_Parser()
        self.headers = {}

        self.DecompressionActions = {
            "not-sent": self.da_not_sent,
            "value-sent": self.da_value_sent,
            "mapping-sent": self.da_mapping_sent,
            "LSB": self.da_lsb,
            "devIID": self.da_dev_iid,
            "appIID": self.da_app_iid,
            "compute-length": self.da_compute_length,
            "compute-checksum": self.da_compute_checksum
        }

    def da_not_sent(self, fid, fl, fp, tv, mo, schc_packet = None, offset = 0):
        self.headers[fid] = tv
        return offset

    def da_value_sent(self, fid, fl, fp, tv, mo, schc_packet = None, offset = 0):
        self.headers[fid] = self.__get_bits(schc_packet, fl, offset)
        return offset + fl

    def da_mapping_sent(self, fid, fl, fp, tv, mo, schc_packet = None, offset = 0):
        max_index = -1
        value = None
        if type(tv) is dict:
            for mappingID, mappingValue in tv.items():
                if mappingID > max_index:
                    max_index = mappingID
        elif type(tv) is list:
            max_index = len(tv) - 1
            
        index_length = 0
        while max_index > 0:
            index_length += 1
            max_index >>= 1

        self.headers[fid] = tv[self.__get_bits(schc_packet, index_length, offset)]
        return offset + index_length

    def da_lsb(self, fid, fl, fp, tv, mo, schc_packet = None, offset = 0):
        shift = fl - int(mo[4:-1])
        self.headers[fid] = (tv << shift) + self.__get_bits(schc_packet, shift, offset)
        return offset + shift

    def da_dev_iid(self, fid, fl, fp, tv, mo, schc_packet = None, offset = 0):
        # based on aes_cmac specified in RFC 4493
        m = bytes([0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88]) # get devEUI
        k = bytes([0x00,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF,0x00,0xAA,0xBB,0xCC,0xDD,0xEE,0xFF,0xAA,0xBB]) # get key
        cipher = AES.new(k, AES.MODE_ECB)

        # subkeys
        rb = 0x87
        k1 = list(cipher.encrypt(binascii.unhexlify("00000000000000000000000000000000")))
        if (k1[0] >> 7) == 0:
            k1 = self.shift_bytes(1, k1 + [0]) # shift left by 1
        else:
            k1 = self.shift_bytes(1, k1 + [0])
            k1[15] = k1[15] ^ rb
        if (k1[0] >> 7) == 0:
            k2 = self.shift_bytes(1, k1 + [0])
        else:
            k2 = self.shift_bytes(1, k1 + [0])
            k2[15] = k1 ^ rb
        
        # m padding and xor-ing
        m = list(m + bytes([0x80,0,0,0,0,0,0,0]))
        for i in range(16):
            m[i] = m[i] ^ k2[i]
        
        # cmac
        cmac = cipher.encrypt(bytes(m))
        self.headers[fid] = int.from_bytes(cmac[:8], "big")

        return offset

    def da_app_iid(self, fid, fl, fp, tv, mo, schc_packet = None, offset = 0):
        raise NotImplementedError

    def da_compute_length(self, fid, fl, fp, tv, schc_packet = None):
        if fid == "IPv6.payloadLength":
            self.headers[fid] = len(schc_packet) + 2 + 2 + 2 + 2 # 2 bytes source port + 2 bytes dest port + 2 bytes checksum + 2 bytes length
        if fid == "UDP.length":
            self.headers[fid] = len(schc_packet) + 2 + 2 + 2 + 2
        return True

    def da_compute_checksum(self, fid, fl, fp, tv, schc_packet = None):
        if fid == "UDP.checksum":
            ipv6_source_address_up = self.headers["IPv6.prefixES"] << 64
            ipv6_source_address_down = self.headers["IPv6.iidES"]
            ipv6_source_address = hex(ipv6_source_address_up | ipv6_source_address_down)[2:]

            ipv6_destination_address_up = self.headers["IPv6.prefixLA"] << 64
            ipv6_destination_address_down = self.headers["IPv6.iidLA"]
            ipv6_destination_address = hex(ipv6_destination_address_up | ipv6_destination_address_down)[2:]

            ipv6_pseudo_header = SCHC_Decompressor.build_pseudo_header(ipv6_source_address, ipv6_destination_address, self.headers["IPv6.nextHeader"], self.headers["UDP.length"])
            buff = ''
            for i in schc_packet:
                buff = buff + struct.pack('>B',i).hex()
            udp_checksum = SCHC_Decompressor.checksum(ipv6_pseudo_header, self.headers["UDP.length"], self.headers["UDP.devPort"], self.headers["UDP.appPort"], buff)
            self.headers[fid] = udp_checksum

    def __get_bits(self, data, length, offset):
        i = offset // 8
        bit_pos = offset % 8
        remain = length % 8
        mask = 0xFF
        val = 0
        
        # full bytes
        for _ in range(length // 8):
            working_byte = ((data[i] << bit_pos) & mask) + (data[i+1] >> (8 - bit_pos))
            val = (val << 8) + working_byte
            i += 1

        # reamining bits
        if remain:
            working_byte = ((data[i] << bit_pos) & mask) + (data[i+1] >> (8 - bit_pos))
            val = (val << remain) + (working_byte >> (8 - remain))

        return val


    def decompress(self, schc_packet, direction):
        # Get RuleID from SCHC Packet
        schc_packet_buff = list(schc_packet)
        rule_id = schc_packet_buff[0]
        # Packet was not compressed
        if rule_id == self.rule_manager.RULE_ID_NOT_COMPRESSED:
            return schc_packet[1:]

        # Get Rule object from RuleID
        rule = self.rule_manager.get_rule_from_id(rule_id)

        # The package is reconstructed using the identifier of the rule
        ip_packet = self.builder(schc_packet_buff, rule, direction)

        return ip_packet

    def shift_bytes(self, offset, array):
        mask = 0xFF
        if offset == 0:
            return array
        shifted = []
        for i in range(len(array)-1):
            #                     higher bits                   lower bits
            shifted.append(((array[i] << offset) & mask) + (array[i+1] >> (8 - offset)))
        return shifted
        

    def builder(self, schc_packet, rule, direction):
        rules_calc = []
        offset = 0
        rule_id = schc_packet.pop(0)
        for r in rule['content']:
            fid = r[0]
            fl = r[1]
            fp = r[2]
            di = r[3]
            tv = r[4]
            mo = r[5]
            cda = r[6]

            if cda == 'compute-length' or cda == 'compute-checksum':
                rules_calc.append(r)
                continue

            if (di is 'Bi') or (di is direction):
                offset = self.DecompressionActions.get(cda)(fid, fl, fp, tv, mo, schc_packet, offset)

        payload = self.shift_bytes(offset % 8, schc_packet[offset//8:])

        for r in rules_calc:
            fid = r[0]
            fl = r[1]
            fp = r[2]
            di = r[3]
            tv = r[4]
            cda = r[6]

            if (di is 'Bi') or (di is direction):
                self.DecompressionActions.get(cda)(fid, fl, fp, tv, payload)

        return SCHC_Parser.build(self.headers, payload, direction)

    @staticmethod
    def checksum(pseudo_header, udp_length, udp_source_port, udp_destination_port, udp_data):
        if (len(udp_data)%4) == 3:
            udp_data = udp_data + '0'
        elif (len(udp_data)%4) == 2:
            udp_data = udp_data + '00'
        elif (len(udp_data)%4) == 1:
            udp_data = udp_data + '000'

        udp_data_sum = 0
        for i in range(0, int(len(udp_data) // 4) ):
            udp_data_sum = int(udp_data[i * 4:i * 4 + 4], 16) + udp_data_sum

        sum_udp = udp_source_port + udp_destination_port + udp_length + udp_data_sum
        sum_total = pseudo_header + sum_udp
        sum_sup = sum_total & 0xFFFF0000
        sum_inf = sum_total & 0x0000FFFF
        sum_final = (sum_sup >> 16) + sum_inf
        result = sum_final ^ int('FFFF', 16)
        return result

    @staticmethod
    def build_pseudo_header(src_ip, dest_ip, next_header, payload_len):
        sum_ipv6_sa = 0
        for i in range(0,int(len(src_ip)//4)):
            sum_ipv6_sa = int(src_ip[i*4:i*4+4],16) + sum_ipv6_sa

        sum_ipv6_da = 0
        for i in range(0,int(len(dest_ip)//4)):
            sum_ipv6_da = int(dest_ip[i*4:i*4+4],16) + sum_ipv6_da

        sum_phdr = sum_ipv6_sa + sum_ipv6_da + next_header + payload_len
        return sum_phdr