import struct
import binascii


class PacketGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate():

        # ****************** IPv6 *************************
        # Enter the value of the headers
        ipv6_version = 0x6
        ipv6_traffic_class = 0x95
        ipv6_flow_label = 0xFDFD3
        ipv6_next_header = 0x11    # UDP
        ipv6_hop_limit = 0x40

        # Mask definition
        mask_high = 0xF0
        mask_low = 0x0F
        mask_flow_label_high = 0xF0000
        mask_flow_label_low = 0x0FFFF

        # byte 0
        ipv6_version = ipv6_version << 4
        traffic_class_hi = ipv6_traffic_class & mask_high
        traffic_class_low = ipv6_traffic_class & mask_low
        traffic_class_hi = traffic_class_hi >> 4
        first_byte = ipv6_version | traffic_class_hi
        first_byte_bf = struct.pack('>B', first_byte)  # bit format
        # print("byte 0: " + binascii.hexlify(first_byte_bf).__str__())

        # byte 1
        traffic_class_low = traffic_class_low << 4
        flow_label_hi = mask_flow_label_high & ipv6_flow_label
        flow_label_hi = flow_label_hi >> 16
        second_byte = traffic_class_low | flow_label_hi
        second_byte_bf = struct.pack('>B', second_byte)  # bit format
        # print("byte 1: " + binascii.hexlify(second_byte_bf).__str__())

        # byte 2 and 3
        third_byte = mask_flow_label_low & ipv6_flow_label
        third_byte_bf = struct.pack('>H', third_byte)  # bit format
        # print("byte 2 - 3: " + binascii.hexlify(third_byte_bf).__str__())

        # byte 6
        sixth_byte_bf = struct.pack('>B', ipv6_next_header)  # bit format
        # print("byte 6: " + binascii.hexlify(sixth_byte_bf).__str__())

        # byte 7
        seventh_byte_bf = struct.pack('>B', ipv6_hop_limit)  # bit format
        # print("byte 7: " + binascii.hexlify(seventh_byte_bf).__str__())

        # byte 8 - 20
        ipv6_source_address = "fc0c0000000000000000000000000094"
        ipv6_source_address_bf = binascii.unhexlify(ipv6_source_address)

        # byte 24 - 36
        ipv6_destination_address = "fc0c0000000000000000000000000008"
        ipv6_destination_address_bf = binascii.unhexlify(ipv6_destination_address)


        # ****************** UDP packet ****************************
        udp_source_port = 32513
        udp_source_port_bf = struct.pack('>H', udp_source_port)

        udp_destination_port = 32640
        udp_destination_port_bf = struct.pack('>H', udp_destination_port)

        udp_data = "07025f0128040015040233"
        udp_data_bf = binascii.unhexlify(udp_data)

        udp_length = len(udp_data_bf) + 8
        udp_length_bf = struct.pack('>H', udp_length)

        # Calculating UDP checksum
        ipv6_pseudo_header = PacketGenerator.build_pseudo_header(ipv6_source_address, ipv6_destination_address, ipv6_next_header, udp_length)
        udp_checksum_bf = PacketGenerator.checksum(ipv6_pseudo_header, udp_length, udp_source_port, udp_destination_port, udp_data)

        # Creating UDP packet
        udp_packet = b''.join([udp_source_port_bf, udp_destination_port_bf, udp_length_bf, udp_checksum_bf, udp_data_bf])

        # ********* IPv6 byte 4 and 5 *********
        ipv6_payload_length = len(udp_packet)
        fourth_fifth_byte_bf = struct.pack('>H', ipv6_payload_length)  # bit format
        # print("byte 4 - 5: " + binascii.hexlify(fourth_fifth_byte_bf).__str__())

        # Creating IPv6 packet
        headers = b''.join([first_byte_bf, second_byte_bf, third_byte_bf, fourth_fifth_byte_bf, sixth_byte_bf, seventh_byte_bf, ipv6_source_address_bf, ipv6_destination_address_bf, udp_source_port_bf, udp_destination_port_bf, udp_length_bf, udp_checksum_bf])
        headers_and_data = b''.join([first_byte_bf, second_byte_bf, third_byte_bf, fourth_fifth_byte_bf, sixth_byte_bf, seventh_byte_bf, ipv6_source_address_bf, ipv6_destination_address_bf, udp_packet])
        print("Packet IPv6: " + str(binascii.hexlify(headers_and_data)))
        print("Lenght: " + str(len(headers_and_data)) + " bytes")
        return (headers_and_data, udp_data_bf, headers)

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
        return struct.pack('>H', result)

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
