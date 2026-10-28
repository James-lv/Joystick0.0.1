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

class BrakeReader:
    def __init__(self, host='127.0.0.1', port=15090, timeout=8):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))
        # 左右脚刹车
        self.axis_mask = AxisBitmask.BrakesLeft  

    def build_get_brake_query(self):
        # 0x40 = Analog inputs
        return struct.pack('<III', 0xD0, self.axis_mask, 0x32)

    def send_then_receive(self, send_data):
        self.sock.sendto(send_data, (self.host, self.port))
        response, _ = self.sock.recvfrom(8192)
        return response

    def read(self):
        try:
            query = self.build_get_brake_query()
            resp = self.send_then_receive(query)
            fmt = '<HB5H9I'
            if(len(resp) == struct.calcsize(fmt)):
                recv_data =  struct.unpack(fmt, resp)
            left_brake = (float)(recv_data[14] / 0xFFFFFFFF);
            right_brake = (float)(recv_data[15] / 0xFFFFFFFF);
            # 数据解析: length, status, node_brakeL, pos_brakeL, node_brakeR, pos_brakeR
            #length, status, node_brakeL, pos_brakeL, node_brakeR, pos_brakeR = struct.unpack('<HBIfIf', resp)
            return {'brake_left': left_brake, 'brake_right': right_brake}
        except Exception as e:
            print("Failed to read brakes:", e)
            return {'brake_left': 0.0, 'brake_right': 0.0}
