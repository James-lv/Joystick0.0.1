#!/usr/bin/env python3

from enum import IntEnum
import socket
import struct
import time
import math

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
    try:
        sock.sendto(send_data, targetAddr)
        response, address = sock.recvfrom(8192)
        return response

    except socket.timeout:
        print("No data received within timeout period.")
        return None

def main():
    sock_cls2sim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_cls2sim.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock_cls2sim.settimeout(8)
    sock_cls2sim.bind(('127.0.0.1', 0))
    remoteEndpoint = ('127.0.0.1', 15090)

    while True:
        # ������(Pitch)����ת(Roll)��ƫ��(Yaw)
        query_readpos = build_get_pos_query(AxisBitmask.Elevator + AxisBitmask.Aileron + AxisBitmask.Rudder)
        pos_response = sendThenReceive(query_readpos, remoteEndpoint, sock_cls2sim)
        if pos_response is not None:
            length, status, node_pitch, pos_pitch, node_roll, pos_roll, node_yaw, pos_yaw = struct.unpack('<HBHfHfHf', pos_response)
            print("\n")
            print("pos_pitch = ", -pos_pitch)
            print("pos_roll = ", pos_roll)
            print("pos_yaw = ", pos_yaw)

        # ������
        query_readbuttons = struct.pack('<III', 0xD0, 0x1, 0x31)
        btns_response = sendThenReceive(query_readbuttons, remoteEndpoint, sock_cls2sim)
        if btns_response is not None:
            payload_len, status = struct.unpack('<HB', btns_response[0:3])
            offset = 3
            while offset < payload_len:
                device_id, num_inputs = struct.unpack('<HH', btns_response[offset:offset+4])
                offset += 4

                num_bytes = math.ceil(num_inputs / 8)
                data = list(struct.unpack('<' + 'B'*num_bytes, btns_response[offset: offset+num_bytes]))
                offset += num_bytes

                print("device_id = ", device_id, "num_bytes = ", num_bytes)

        time.sleep(0.05)

if __name__ == "__main__":
    main()
