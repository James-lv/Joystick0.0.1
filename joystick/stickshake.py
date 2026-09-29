##!/usr/bin/env python3
#import socket
#import struct
#
#class stickshakercon:
#    def __init__(self, host='127.0.0.1', port=15090, timeout=0.01):
#        self.host = host
#        self.port = port
#        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 10)
#        self.sock.settimeout(timeout)
#        self.sock.bind(('', 0))
#        
#    
#    def prepare_axis(self, axis_mask):
#        query_override = struct.pack('<III', 0xD1, axis_mask, 0x5)
#        self.sock.sendto(query_override, (self.host, self.port))
#
#    def set_force(self, force, freq):
#        fe = 1000/freq 
#        query_speed = struct.pack('<IIII', 0xCE, 0x1, 0xC1, int(fe))
#        query_force = struct.pack('<IIII', 0xCE, 0x1, 0xC2, int(force))
#        self.sock.sendto(query_speed, (self.host, self.port))
#        self.sock.sendto(query_force, (self.host, self.port))
#        
#    def enable(self, enable):
# #       """启用振动"""
#        query_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0,enable)
#        self.sock.sendto(query_enable, (self.host, self.port))
#        
#
#    def disable(self, disenble):
# #       """停止振动"""
#        query_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, disenble)
#        self.sock.sendto(query_disable, (self.host, self.port))
       
    
#!/usr/bin/env python3
import socket
import struct
import time
class stickshakercon:
    def __init__(self, host='127.0.0.1', port=15090, timeout=0.1):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,15)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))
        query_override = struct.pack('<III', 0xD1, 0x3, 0x5)
        self.sock.sendto(query_override, (self.host, self.port))
        # 开启外部控制权限 (Override)
        
        



    def set_force(self, F=50, freq=10):
 #       """设置振动参数 force: 振动力量 freq: 振动频率 (ms)"""
        fe = 300
        FORCE=20
        query_speed = struct.pack('<IIII', 0xCE, 0x1, 0xC1, int(fe))
        query_force = struct.pack('<IIII', 0xCE, 0x1, 0xC2, int(FORCE))
        self.sock.sendto(query_speed, (self.host, self.port))
        self.sock.sendto(query_force, (self.host, self.port))
       


    def enable(self):
 #       """启用振动"""
       
        
        query_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 1)
        self.sock.sendto(query_enable, (self.host, self.port))
        res, address = self.sock.recvfrom(8192)
        print("res:", res)
        print("recv_time:", time.time())

    def disable(self):
 #       """停止振动"""
        query_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 0)
        self.sock.sendto(query_disable, (self.host, self.port))
        resp, address = self.sock.recvfrom(8192)
        print("resp:", resp)
        print("recv_time:", time.time())
        