#!/usr/bin/env python3

import socket
import struct
import math
import time

def main():
    timeout = 8
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock.settimeout(timeout)
    sock.bind(('', 0))

    remoteEndpoint = ('127.0.0.1', 15090)
    query_readbuttons = struct.pack('<III', 0xD0, 0x1, 0x31)

    # 打印表头一次
    print(f"{'DeviceID':>8} | {'NumInputs':>9} | {'Data':>20}")

    # 初始化标志
    first_loop = True

    while True:
        sock.sendto(query_readbuttons, remoteEndpoint)
        response, address = sock.recvfrom(8192)

        payload_len, status = struct.unpack('<HB', response[0:3])
        offset = 3

        output_line = ""  # 保存设备4的输出

        while offset < payload_len:
            device_id, num_inputs = struct.unpack('<HH', response[offset:offset+4])
            offset += 4

            num_bytes = math.ceil(num_inputs / 8)
            data = list(struct.unpack('<' + 'B'*num_bytes, response[offset: offset+num_bytes]))
            offset += num_bytes

            if device_id == 4:
                output_line = f"{device_id:8} | {num_inputs:9} | {str(data):>20}"

        # 原地刷新设备4状态
        if not first_loop:
            print("\033[1F\033[2K", end='')  # 上移一行并清空
        else:
            first_loop = False

        # 打印设备4状态
        print(output_line)

        time.sleep(0.05)

if __name__ == "__main__":
    main()
