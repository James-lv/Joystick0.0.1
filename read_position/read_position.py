#!/usr/bin/env python3
from enum import IntEnum
import socket
import struct
import time

# ==== Axis bitmask ====
class AxisBitmask(IntEnum):
    Elevator     = 0x1
    Aileron      = 0x2
    Rudder       = 0x4
    Collective   = 0x8
    BrakesLeft   = 0x10
    BrakesRight  = 0x20
    TrimElevator = 0x40
    TrimAileron  = 0x80
    TrimRudder   = 0x100
    Throttle1    = 0x200
    Throttle2    = 0x400
    Throttle3    = 0x800
    Throttle4    = 0x1000
    SpeedBrake   = 0x2000
    NoseWheel    = 0x4000
    Seatshaker   = 0x8000

# ==== Build query command ====
def build_get_pos_query(axis):
    return struct.pack('<III', 0xD0, axis, 0x11)

# ==== Send and receive UDP ====
def sendThenReceive(send_data, targetAddr, sock):
    sock.sendto(send_data, targetAddr)
    response, address = sock.recvfrom(8192)
    return response

def main():
    timeout = 8
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock.settimeout(timeout)
    sock.bind(('', 0))

    remoteEndpoint = ('127.0.0.1', 15090)

    # 只读俯仰(Pitch)、滚转(Roll)、偏航(Yaw)
    query_readpos = build_get_pos_query(AxisBitmask.Elevator + AxisBitmask.Aileron + AxisBitmask.Rudder)

    # 打印 Hex response 只显示一次
    pos_response = sendThenReceive(query_readpos, remoteEndpoint, sock)
    print("Hex response:", pos_response.hex())

    # 打印表头
    print(f"{'Pos Pitch':>10} | {'Pos Roll':>10} | {'Pos Yaw':>10}")

    while True:
        pos_response = sendThenReceive(query_readpos, remoteEndpoint, sock)
        length, status, node_pitch, pos_pitch, node_roll, pos_roll, node_yaw, pos_yaw = struct.unpack('<HBHfHfHf', pos_response)
        
        # 实时刷新一行数值
        print(f"{-pos_pitch:10.6f} | {pos_roll:10.6f} | {pos_yaw:10.6f}", end='\r', flush=True)

        # 控制刷新频率
        time.sleep(0.05)

if __name__ == "__main__":
    main()
