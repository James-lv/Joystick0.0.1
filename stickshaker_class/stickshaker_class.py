#!/usr/bin/env python3
import socket
import struct

class stickshaker_class:
    def __init__(self, host='127.0.0.1', port=15090, timeout=8):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))

        # 开启外部控制权限 (Override)
        query_override = struct.pack('<III', 0xD1, 0x3, 0x5)
        self.sock.sendto(query_override, (self.host, self.port))
        self.sock.recvfrom(8192)  # 忽略返回

    def set_force(self, force=50, freq=100):
        """
        设置振动参数
        force: 振动力量
        freq: 振动频率 (ms)
        """
        interval_100qs_units = freq * 10
        query_speed = struct.pack('<IIII', 0xCE, 0x1, 0xC1, interval_100qs_units)
        query_force = struct.pack('<IIII', 0xCE, 0x1, 0xC2, force)
        self.sock.sendto(query_speed, (self.host, self.port))
        self.sock.recvfrom(8192)
        self.sock.sendto(query_force, (self.host, self.port))
        self.sock.recvfrom(8192)

    def enable(self):
        """启用振动"""
        query_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 1)
        self.sock.sendto(query_enable, (self.host, self.port))
        self.sock.recvfrom(8192)

    def disable(self):
        """停止振动"""
        query_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 0)
        self.sock.sendto(query_disable, (self.host, self.port))
        self.sock.recvfrom(8192)

