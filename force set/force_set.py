#!/usr/bin/env python3
from enum import IntEnum
import socket
import struct
import math
import time

# ===================== Axis 定义 =====================
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

# ===================== UDP 命令封装 =====================
def build_set_force_profile_query(axis, forces):
    return struct.pack(
        '<IIIHHHHHHHHH',
        0xCE, axis, 0x10,
        forces[0], forces[1], forces[2], forces[3], forces[4],
        forces[5], forces[6], forces[7], forces[8]
    )

def build_set_profile_mode_query(axis, mode):
    return struct.pack('<IIIb', 0xCE, axis, 0x30, mode)

def build_set_force_scale_fact_query(axis, scaling):
    return struct.pack('<IIIH', 0xCE, axis, 0x20, scaling)

def sendThenReceive(send_data, targetAddr, sock):
    sock.sendto(send_data, targetAddr)
    response, address = sock.recvfrom(8192)
    return response

# ===================== 主程序 =====================
def main():
    timeout = 8
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock.settimeout(timeout)
    sock.bind(('', 0))

    # CLS2Sim 监听地址
    remoteEndpoint = ('127.0.0.1', 15090)

    # 单独为 Elevator 设置
    elevator_forces = [32, 398, 958, 1018, 1333, 2081, 2484, 2651, 2666]
    sendThenReceive(build_set_force_profile_query(AxisBitmask.Elevator, elevator_forces), remoteEndpoint, sock)
    sendThenReceive(build_set_profile_mode_query(AxisBitmask.Elevator, 1), remoteEndpoint, sock)

    # 单独为 Aileron 设置
    aileron_forces = [30, 350, 900, 1000, 1300, 2000, 2400, 2600, 2700]
    sendThenReceive(build_set_force_profile_query(AxisBitmask.Aileron, aileron_forces), remoteEndpoint, sock)
    sendThenReceive(build_set_profile_mode_query(AxisBitmask.Aileron, 1), remoteEndpoint, sock)

    print("✅ Elevator & Aileron Force Profile & Mode 已初始化")

    # ----------- 动态调整 Scaling -----------
    while True:
        scaling_elevator = 100
        scaling_aileron = 100
        sendThenReceive(build_set_force_scale_fact_query(AxisBitmask.Elevator, scaling_elevator), remoteEndpoint, sock)
        sendThenReceive(build_set_force_scale_fact_query(AxisBitmask.Aileron, scaling_aileron), remoteEndpoint, sock)
        time.sleep(0.05)

    sock.close()

if __name__ == "__main__":
    main()

