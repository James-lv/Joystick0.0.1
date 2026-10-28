#!/usr/bin/env python3
import socket
import struct
from enum import IntEnum

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


class ForceProfileController:
    def __init__(self, host="127.0.0.1", port=15090, timeout=2):
        self.HOST = host
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))  # 本地随机端口

    # ----------- 内部方法 -----------
    def _send_then_receive(self, send_data):
        self.sock.sendto(send_data, (self.HOST, self.PORT))
        try:
            response, _ = self.sock.recvfrom(8192)
            return response
        except socket.timeout:
            return None

    def _build_set_force_profile(self, axis, forces):
        return struct.pack(
            '<IIIHHHHHHHHH',
            0xCE, axis, 0x10,
            forces[0], forces[1], forces[2], forces[3], forces[4],
            forces[5], forces[6], forces[7], forces[8]
        )

    def _build_set_profile_mode(self, axis, mode):
        return struct.pack('<IIIb', 0xCE, axis, 0x30, mode)

    def _build_set_scale_factor(self, axis, scaling):
        return struct.pack('<IIIH', 0xCE, axis, 0x20, scaling)

    # ----------- 对外接口 -----------
    def set_axis_force_profile(self, axis, forces, mode=1):
       # """一次性设置 Force Profile + 模式"""
        self._send_then_receive(self._build_set_force_profile(axis, forces))
        self._send_then_receive(self._build_set_profile_mode(axis, mode))

    def set_axis_scaling(self, axis, scaling):
       # """动态设置 Scaling"""
        self._send_then_receive(self._build_set_scale_factor(axis, scaling))

    def close(self):
        self.sock.close()
