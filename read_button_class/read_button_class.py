#!/usr/bin/env python3
import socket
import struct
import math
import time

class ButtonReader:
    def __init__(self, host='127.0.0.1', port=15090, device_id=4, timeout=8):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))
        self.query_readbuttons = struct.pack('<III', 0xD0, 0x1, 0x31)

    def read(self):
        """
        读取指定设备的按钮状态，返回列表，每个元素为0或1
        """
        try:
            self.sock.sendto(self.query_readbuttons, (self.host, self.port))
            response, _ = self.sock.recvfrom(8192)

            payload_len, status = struct.unpack('<HB', response[0:3])
            offset = 3

            output_data = []

            while offset < payload_len:
                dev_id, num_inputs = struct.unpack('<HH', response[offset:offset+4])
                offset += 4

                num_bytes = math.ceil(num_inputs / 8)
                data = list(struct.unpack('<' + 'B'*num_bytes, response[offset:offset+num_bytes]))
                offset += num_bytes

                if dev_id == self.device_id:
                    output_data = data

            return output_data

        except Exception as e:
            print("Failed to read buttons:", e)
            return []

