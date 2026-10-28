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


# ===================== Force Offset 控制类 =====================
class ForceOffsetController:
    #"""控制 CLS2Sim 的 Force offset 参数"""

    def __init__(self, ip="127.0.0.1", port=15090, timeout=1):
        self.remoteEndpoint = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))

    # ===================== 内部构建命令 =====================
    def _build_override_cmd(self, axis):
        return struct.pack('<III', 0xD1, axis, 0x5)

    def _build_force_offset_cmd(self, axis, force_value):
        return struct.pack('<IIIi', 0xCE, axis, 0xD0, force_value)

    def _sendThenReceive(self, data):
        self.sock.sendto(data, self.remoteEndpoint)
        response, _ = self.sock.recvfrom(8192)
        return response

    # ===================== 统一接口 =====================
    def set_force_offset(self, axis_name: str, force_value: int):
        axis = getattr(AxisBitmask, axis_name)
        # Step 1️⃣ 启用 override
        override_cmd = self._build_override_cmd(axis)
        override_resp = self._sendThenReceive(override_cmd)
        #print(f"[Override] {axis_name} -> response: {override_resp}")
        # Step 2️⃣ 设置 Force offset
        offset_cmd = self._build_force_offset_cmd(axis, force_value)
        offset_resp = self._sendThenReceive(offset_cmd)
        #print(f"[ForceOffset] {axis_name} = {force_value} -> response: {offset_resp}")
        return offset_resp

    def set_multiple_areo(self, areo_dict: dict):
        for axis, pos in areo_dict.items():
            self.set_force_offset(axis, pos)



    def close(self):
        self.sock.close()