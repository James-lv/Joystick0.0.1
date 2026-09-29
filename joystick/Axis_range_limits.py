#!/usr/bin/env python3
import socket
import struct
from enum import IntEnum


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


class AxisRangeController:
    #"""控制 CLS2Sim 的 Axis Range Limits"""

    def __init__(self, ip="127.0.0.1", port=15090, timeout=8):
        self.remoteEndpoint = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))

    # ===================== UDP 命令构建 =====================
    

    def _sendThenReceive(self, send_data: bytes):
        self.sock.sendto(send_data, self.remoteEndpoint)
        response, _ = self.sock.recvfrom(8192)
        return response

    # ===================== 对外接口 =====================
    def set_axis_range(self, axis_name: str, value):
        #"""通过轴名称设置范围限制"""
        axis = getattr(AxisBitmask, axis_name)
        query = struct.pack('<IIIii', 0xCE, axis, 0x95, value[0], value[1])
        response = self._sendThenReceive(query)
        print(f"[AxisRange] {axis_name} -> [{value[0]}, {value[1]}] -> response: {response}")
        return response

    def close(self):
        self.sock.close()