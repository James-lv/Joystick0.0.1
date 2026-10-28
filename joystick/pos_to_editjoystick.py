#!/usr/bin/env python3
from enum import IntEnum
import socket
import struct
import time

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

class PosReader_raw:
    def __init__(self, host='127.0.0.1', port=15090, timeout=8):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))
        # 读取 Elevator, Aileron, Rudder
        self.axis_mask = AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder 

    def build_get_pos_query(self):
        return struct.pack('<III', 0xD0, self.axis_mask, 0x12)

    def send_then_receive(self, send_data):
        self.sock.sendto(send_data, (self.host, self.port))
        response, _ = self.sock.recvfrom(8192)
        return response

    def read(self):
      #  """返回当前轴位置字典:{'pitch': float, 'roll': float, 'yaw': float}"""
        try:
            query = self.build_get_pos_query()
            resp = self.send_then_receive(query)
            # 数据解析: length, status, node_pitch, pos_pitch, node_roll, pos_roll, node_yaw, pos_yaw
            length, status, node_pitch, pos_pitch, node_roll, pos_roll, node_yaw, pos_yaw = struct.unpack('<HBHiHiHi', resp)
            #pos_pitch,pos_roll,pos_yaw = struct.unpack('<fff', resp)
            return {'pitch_raw': -pos_pitch, 'roll_raw': -pos_roll, 'yaw_raw': -pos_yaw}
        except Exception as e:
            print("Failed to read positions:", e)
            return {'pitch': 0, 'roll': 0, 'yaw': 0}

