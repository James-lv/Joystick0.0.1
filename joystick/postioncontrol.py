#!/usr/bin/env python3
import socket
import struct
from enum import IntEnum

class Axis(IntEnum):
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

SETTING_AUTOPILOT_FORCE    = 0x50
SETTING_AUTOPILOT_SPEED    = 0x60
SETTING_AUTOPILOT_ENABLE   = 0x70
SETTING_AUTOPILOT_POSITION = 0x80

class PositionControl:
    def __init__(self, host="127.0.0.1", port=15090):
        self.HOST = host
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)
        
    
    def prepare_axis(self, axis_mask):
        """Prepare axis: set force and speed, do not enable automatically."""
        packet_force = struct.pack('<IIIH', 0xCE, axis_mask, SETTING_AUTOPILOT_FORCE, 20000)
        self.sock.sendto(packet_force, (self.HOST, self.PORT))
        packet_speed = struct.pack('<IIIH', 0xCE, axis_mask, SETTING_AUTOPILOT_SPEED, 1000)
        self.sock.sendto(packet_speed, (self.HOST, self.PORT))

    # ------------------- 核心功能 -------------------
    def enable_pos_contr_class(self, axis,Value):
        """Enable/disable position control."""
        packet_enable = struct.pack('<IIIB', 0xCE, axis, SETTING_AUTOPILOT_ENABLE ,Value)
        self.sock.sendto(packet_enable, (self.HOST, self.PORT))
        

    def move_axis_to_position(self, axis_mask, position):
        """Move axis to position (-1.0 .. 1.0)."""
        packet_move = struct.pack("<IIIf" , 0xCE, axis_mask, SETTING_AUTOPILOT_POSITION, float(position))
        self.sock.sendto(packet_move, (self.HOST, self.PORT))

    #def build_get_pos_query(self, axis_mask):
    #    """Build query packet for current position."""
    #    return struct.pack("<III", 0xD0, axis_mask, 0x11)

    #def read_pos_classs(self):
    #    """Read current normalized position of Elevator + Aileron + Rudder."""
    #    axis_mask = AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder
    #    query = self.build_get_pos_query(axis_mask)
    #    self.sock.sendto(query, (self.HOST, self.PORT))
    #    try:
    #        data,_= self.sock.recvfrom(8192)
    #        # 每个轴返回: 1B node + 4B float
    #        length, status, node_pitch, pos_pitch, node_roll, pos_roll,node_yaw, pos_yaw = struct.unpack('<HBHfHfHf', data)
    #        print("length:", len(data))
    #        return {'pitch': -pos_pitch, 'roll': pos_roll, 'yaw': pos_yaw}  # 返回 [(node, pos), ...]，顺序 Elevator, Aileron, Rudder
    #    except Exception as e:
    #        print("Failed to parse position response:", e)
    #        return None
    # ------------------- 高级接口 -------------------
    def set_target_positions(self, elevator_pos, aileron_pos, rudder_pos):
        """Set Elevator, Aileron, Rudder positions (-1.0..1.0)."""
        self.move_axis_to_position(Axis.Elevator, -elevator_pos)
        self.move_axis_to_position(Axis.Aileron, -aileron_pos)
        self.move_axis_to_position(Axis.Rudder, -rudder_pos)
        #return self.read_pos_classs()
    #-----------------picth+pos------------------------
    def set_target_p_position(self, elevator_pos):
        """Set Elevator, Aileron, Rudder positions (-1.0..1.0)."""
        self.move_axis_to_position(Axis.Elevator, -elevator_pos)
        #return self.read_pos_classs()
