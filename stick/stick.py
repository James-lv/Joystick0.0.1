#!/usr/bin/env python3

from enum import IntEnum
import socket
import struct
import time

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
    response = None
    try:
        sock.sendto(send_data, targetAddr)
        response, address = sock.recvfrom(8192)
    except socket.timeout:
        print("No data received within timeout period.")

    return response

def main():
    # 创建与cls2sim通信的socket
    sock_cls2sim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_cls2sim.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock_cls2sim.settimeout(8)
    sock_cls2sim.bind(('127.0.0.1', 0))
    cls2sim_remoteEndpoint = ('127.0.0.1', 15090)

    # 创建与主机通信的socket
    sock_host = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_host.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock_host.settimeout(8)
    sock_host.bind(('127.0.0.1', 13000)) # 跟据项目实际修改
    host_remoteEndpoint = ('127.0.0.1', 13000) # 跟据项目实际修改

    # 3.振杆
    # 开启外部控制权限 (Override)
    query_setvibration_override = struct.pack('<III', 0xD1, 0x3, 0x5)
    sock_cls2sim.sendto(query_setvibration_override, cls2sim_remoteEndpoint)
    # response, address = sock.recvfrom(8192)


    while True:
        # 1.读俯仰(Pitch)、滚转(Roll)、偏航(Yaw)
        query_readpos = build_get_pos_query(AxisBitmask.Elevator + AxisBitmask.Aileron + AxisBitmask.Rudder)
        pos_response = sendThenReceive(query_readpos, cls2sim_remoteEndpoint, sock_cls2sim)
        if pos_response is not None:
            length, status, node_pitch, pos_pitch, node_roll, pos_roll, node_yaw, pos_yaw = struct.unpack('<HBHfHfHf', pos_response)
            print("\n")
            print("pos_pitch = ", pos_pitch)
            print("pos_roll = ", pos_roll)
            print("pos_yaw = ", pos_yaw)

        # 2.读按键
        query_readbuttons = struct.pack('<III', 0xD0, 0x1, 0x31)
        btns_response = sendThenReceive(query_readbuttons, cls2sim_remoteEndpoint, sock_cls2sim)
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

        # 3.振杆启用或禁用
        host_response = None
        try:
            host_response, address = sock_host.recvfrom(8192)
        except socket.timeout:
                print("No data received within timeout period.")

        if host_response is None:
            continue

        host_response_len = len(host_response)
        if host_response_len < 4: 
            continue

        # cmd: 1：振杆，2：杆位置反驱 3：杆力反馈
        length, cmd, sub_cmd = struct.unpack('<HBB', host_response)
        offset = 4

        # 振杆
        if cmd == 0x01 and sub_cmd == 0x01: # 设置力和频率
            vibration_force, vibration_freq = struct.unpack('<II', host_response[offset:offset+8])
            
            interval_100qs_units = vibration_freq*10
            query_setvibration_speed_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC1, interval_100qs_units)
            sock_cls2sim.sendto(query_setvibration_speed_fast, cls2sim_remoteEndpoint)
            # response, address = sock.recvfrom(8192)

            query_setvibration_force_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC2, vibration_force)
            sock_cls2sim.sendto(query_setvibration_force_fast, cls2sim_remoteEndpoint)
            # response, address = sock.recvfrom(8192)
        # 振杆
        if cmd == 0x01 and sub_cmd == 0x02: # 启动振动or停止振动
            # 预定义 enable/disable 指令
            query_setvibration_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 1)
            query_setvibration_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 0)

            enable = struct.unpack('<B', host_response[offset:offset+1])
            bEnable = bool(enable)
            if bEnable:
                sock_cls2sim.sendto(query_setvibration_enable, cls2sim_remoteEndpoint)
                print("v on")
            else:
                sock_cls2sim.sendto(query_setvibration_disable, cls2sim_remoteEndpoint)
                print("v off")

        time.sleep(0.05)

if __name__ == "__main__":
    main()

