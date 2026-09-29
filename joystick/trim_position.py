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


class TrimController:
    def __init__(self, remote_ip='127.0.0.1', remote_port=15090, timeout=8):
        self.remote_endpoint = (remote_ip, remote_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))
        #print(f"[INFO] TrimController initialized. Target = {self.remote_endpoint}")

    
    def build_trim_command(self,axis: AxisBitmask, trim_position: float):
        return struct.pack('<IIIf', 0xCE, axis, 0x90, trim_position)

    def send_then_receive(self, data: bytes):
        self.sock.sendto(data, self.remote_endpoint)
        response, address = self.sock.recvfrom(8192)
        return response
    
    def set_trim_position(self, axis: AxisBitmask, position: float):
        #print(f"[SEND] {locals()}")
        cmd = self.build_trim_command(axis, position)
        response = self.send_then_receive(cmd)
        #print(f"[SEND] {axis.name} trim = {position}")
        #print(f"[RECV] ({len(response)} bytes): {response.hex()}")
        return response

    def set_multiple_trim_positions(self, trim_dict: dict):
        for axis, pos in trim_dict.items():
            self.set_trim_position(axis, pos)

    def close(self):
        self.sock.close()
        print("[INFO] TrimController closed.")
