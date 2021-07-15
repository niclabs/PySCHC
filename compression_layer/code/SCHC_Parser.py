class SCHC_Parser:

    def __init__(self):
        self.header_fields = {}
        self.udp_data = []
        self.unparsed_headers = []

    def parser(self, buffer, direction):
        data_buffer = list(buffer)

        # Mask definition
        mask_high = int('F0', 16)
        mask_low = int('0F', 16)

        # validating if it is an ipv6 package
        if (data_buffer[0] >> 4) == 6:
            self.header_fields["IPv6.version", 1] = [data_buffer[0] >> 4, "fixed"]
            self.header_fields["IPv6.trafficClass", 1] = [(data_buffer[0] << 4) & mask_high | (data_buffer[1] >> 4) & mask_low, "fixed"]
            self.header_fields["IPv6.flowLabel", 1] = [(data_buffer[1] & mask_low) << 16 | data_buffer[2] << 8 | data_buffer[3], "fixed"]
            self.header_fields["IPv6.payloadLength", 1] = [data_buffer[4] << 8 | data_buffer[5], "fixed"]
            self.header_fields["IPv6.nextHeader", 1] = [data_buffer[6], "fixed"]
            self.header_fields["IPv6.hopLimit", 1] = [data_buffer[7], "fixed"]
            if direction == "Up":
                dp = 8 # dev byte position
                ap = 24 # app byte position
            elif direction == "Down":
                dp = 24 # dev byte position
                ap = 8 # app byte position
            else:
                print("Unrecognized direction")
                return False
            self.header_fields["IPv6.devPrefix", 1] = [data_buffer[dp+0] << 56 | data_buffer[dp+1] << 48 | data_buffer[dp+2] << 40 | data_buffer[dp+3] << 32 | data_buffer[dp+4] << 24 | data_buffer[dp+5] << 16 | data_buffer[dp+6] << 8 | data_buffer[dp+7], "fixed"]
            self.header_fields["IPv6.devIID", 1] = [data_buffer[dp+8] << 56 | data_buffer[dp+9] << 48 | data_buffer[dp+10] << 40 | data_buffer[dp+11] << 32 | data_buffer[dp+12] << 24 | data_buffer[dp+13] << 16 | data_buffer[dp+14] << 8 | data_buffer[dp+15], "fixed"]
            self.header_fields["IPv6.appPrefix", 1] = [data_buffer[ap+0] << 56 | data_buffer[ap+1] << 48 | data_buffer[ap+2] << 40 | data_buffer[ap+3] << 32 | data_buffer[ap+4] << 24 | data_buffer[ap+5] << 16 | data_buffer[ap+6] << 8 | data_buffer[ap+7], "fixed"]
            self.header_fields["IPv6.appIID", 1] = [data_buffer[ap+8] << 56 | data_buffer[ap+9] << 48 | data_buffer[ap+10] << 40 | data_buffer[ap+11] << 32 | data_buffer[ap+12] << 24 | data_buffer[ap+13] << 16 | data_buffer[ap+14] << 8 | data_buffer[ap+15], "fixed"]

            if self.header_fields["IPv6.nextHeader", 1][0] == 17:
                self.header_fields["UDP.devPort", 1] = [data_buffer[40] << 8 | data_buffer[41], "fixed"]
                self.header_fields["UDP.appPort", 1] = [data_buffer[42] << 8 | data_buffer[43], "fixed"]
                self.header_fields["UDP.length", 1] = [data_buffer[44] << 8 | data_buffer[45], "fixed"]
                self.header_fields["UDP.checksum", 1] = [data_buffer[46] << 8 | data_buffer[47], "fixed"]
                self.udp_data = [data_buffer[48:len(data_buffer)], "variable"]
                self.unparsed_headers = data_buffer[:48]

            else:
                print("Unsupported L4 protocol")
        else:
            print("The message is not an IPv6 package")
            return False

        return True

    @staticmethod
    def build(headers, payload, direction):
        data_buffer = bytearray(48)

        # Mask definition
        mask_byte = int('FF', 16)
        mask_low = int('0F', 16)

        # IPv6 Header
        # version
        data_buffer[0] = headers["IPv6.version"] << 4
        
        # traffic class
        data_buffer[0] += headers["IPv6.trafficClass"] >> 4
        data_buffer[1] = (headers["IPv6.trafficClass"] & mask_low) << 4
        
        # flow label
        data_buffer[1] += headers["IPv6.flowLabel"] >> 16
        data_buffer[2] = (headers["IPv6.flowLabel"] >> 8) & mask_byte
        data_buffer[3] = headers["IPv6.flowLabel"] & mask_byte

        # payload length
        data_buffer[4] = headers["IPv6.payloadLength"] >> 8
        data_buffer[5] = headers["IPv6.payloadLength"] & mask_byte

        # next header
        data_buffer[6] = headers["IPv6.nextHeader"]

        # hop limit
        data_buffer[7] = headers["IPv6.hopLimit"]

        if direction == "Up":
            dp = 8 # dev byte position
            ap = 24 # app byte position
        elif direction == "Down":
            dp = 24 # dev byte position
            ap = 8 # app byte position
        else:
            print("Unrecognized direction")
            return False
        # source address
        data_buffer[dp+0] = headers["IPv6.devPrefix"] >> 56
        data_buffer[dp+1] = (headers["IPv6.devPrefix"] >> 48) & mask_byte
        data_buffer[dp+2] = (headers["IPv6.devPrefix"] >> 40) & mask_byte
        data_buffer[dp+3] = (headers["IPv6.devPrefix"] >> 32) & mask_byte
        data_buffer[dp+4] = (headers["IPv6.devPrefix"] >> 24) & mask_byte
        data_buffer[dp+5] = (headers["IPv6.devPrefix"] >> 16) & mask_byte
        data_buffer[dp+6] = (headers["IPv6.devPrefix"] >> 8) & mask_byte
        data_buffer[dp+7] = headers["IPv6.devPrefix"] & mask_byte

        data_buffer[dp+8] = headers["IPv6.devIID"] >> 56
        data_buffer[dp+9] = (headers["IPv6.devIID"] >> 48) & mask_byte
        data_buffer[dp+10] = (headers["IPv6.devIID"] >> 40) & mask_byte
        data_buffer[dp+11] = (headers["IPv6.devIID"] >> 32) & mask_byte
        data_buffer[dp+12] = (headers["IPv6.devIID"] >> 24) & mask_byte
        data_buffer[dp+13] = (headers["IPv6.devIID"] >> 16) & mask_byte
        data_buffer[dp+14] = (headers["IPv6.devIID"] >> 8) & mask_byte
        data_buffer[dp+15] = headers["IPv6.devIID"] & mask_byte

        # destination address
        data_buffer[ap+0] = headers["IPv6.appPrefix"] >> 56
        data_buffer[ap+1] = (headers["IPv6.appPrefix"] >> 48) & mask_byte
        data_buffer[ap+2] = (headers["IPv6.appPrefix"] >> 40) & mask_byte
        data_buffer[ap+3] = (headers["IPv6.appPrefix"] >> 32) & mask_byte
        data_buffer[ap+4] = (headers["IPv6.appPrefix"] >> 24) & mask_byte
        data_buffer[ap+5] = (headers["IPv6.appPrefix"] >> 16) & mask_byte
        data_buffer[ap+6] = (headers["IPv6.appPrefix"] >> 8) & mask_byte
        data_buffer[ap+7] = headers["IPv6.appPrefix"] & mask_byte

        data_buffer[ap+8] = headers["IPv6.appIID"] >> 56
        data_buffer[ap+9] = (headers["IPv6.appIID"] >> 48) & mask_byte
        data_buffer[ap+10] = (headers["IPv6.appIID"] >> 40) & mask_byte
        data_buffer[ap+11] = (headers["IPv6.appIID"] >> 32) & mask_byte
        data_buffer[ap+12] = (headers["IPv6.appIID"] >> 24) & mask_byte
        data_buffer[ap+13] = (headers["IPv6.appIID"] >> 16) & mask_byte
        data_buffer[ap+14] = (headers["IPv6.appIID"] >> 8) & mask_byte
        data_buffer[ap+15] = headers["IPv6.appIID"] & mask_byte

        # UDP Header
        # source port
        data_buffer[40] = headers["UDP.devPort"] >> 8
        data_buffer[41] = headers["UDP.devPort"] & mask_byte

        # destination port
        data_buffer[42] = headers["UDP.appPort"] >> 8
        data_buffer[43] = headers["UDP.appPort"] & mask_byte

        # length
        data_buffer[44] = headers["UDP.length"] >> 8
        data_buffer[45] = headers["UDP.length"] & mask_byte

        # checksum
        data_buffer[46] = headers["UDP.checksum"] >> 8
        data_buffer[47] = headers["UDP.checksum"] & mask_byte

        return bytes(data_buffer) + bytes(payload)
