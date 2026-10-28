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


# ===================== P Move Back 控制类 =====================
class PMoveBackController:
    #"""控制 CLS2Sim 的 P Move Back 参数"""
    def __init__(self, ip="127.0.0.1", port=15090, timeout=8):
        self.remoteEndpoint = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))

    # ===================== UDP 命令构建 =====================
    def _build_pmoveback_query(self, axis, value: int):
        #"""构建设置 P Move Back 的 UDP 命令"""
        return struct.pack('<IIII', 0xCE, axis, 0xD3, value)

    def _sendThenReceive(self, send_data: bytes):
        #"""发送命令并接收响应"""
        self.sock.sendto(send_data, self.remoteEndpoint)
        response, _ = self.sock.recvfrom(8192)
        return response

    # ===================== 对外接口 =====================
    def set_pmoveback(self, axis_name: str, value: int):
       # """通过轴名称设置 P Move Back 值"""
        axis = getattr(AxisBitmask, axis_name)
        query = self._build_pmoveback_query(axis, value)
        response = self._sendThenReceive(query)
        #print(f"[P Move Back] {axis_name} = {value} -> response: {response}")
        return response

    def close(self):
        self.sock.close()