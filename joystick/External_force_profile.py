# from enum import IntEnum
# import socket
# import struct

# # ===================== Axis 定义 =====================
# class AxisBitmask(IntEnum):
#     Elevator     = 0x1
#     Aileron      = 0x2
#     Rudder       = 0x4
#     Collective   = 0x8
#     BrakesLeft   = 0x10
#     BrakesRight  = 0x20
#     TrimElevator = 0x40
#     TrimAileron  = 0x80
#     TrimRudder   = 0x100
#     Throttle1    = 0x200
#     Throttle2    = 0x400
#     Throttle3    = 0x800
#     Throttle4    = 0x1000
#     SpeedBrake   = 0x2000
#     NoseWheel    = 0x4000
#     Seatshaker   = 0x8000


# class ForceProfileManager:
#     def __init__(self, ip: str = "127.0.0.1", port: int = 15090, timeout: int = 8):
#         self.remoteEndpoint = (ip, port)
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
#         self.sock.settimeout(timeout)
#         self.sock.bind(('', 0))
        

#     # ===================== UDP 命令构建 =====================
#     def _build_set_extended_force_profile_query(self, force_profile_positive, pos_positive,
#                                                 force_profile_negative, pos_negative, axis):
#         return struct.pack(
#             '<III' + ('Hi' * 18),
#             0xCE, axis, 0xE0,
#             force_profile_positive[0], int(pos_positive[0]),
#             force_profile_positive[1], int(pos_positive[1]),
#             force_profile_positive[2], int(pos_positive[2]),
#             force_profile_positive[3], int(pos_positive[3]),
#             force_profile_positive[4], int(pos_positive[4]),
#             force_profile_positive[5], int(pos_positive[5]),
#             force_profile_positive[6], int(pos_positive[6]),
#             force_profile_positive[7], int(pos_positive[7]),
#             force_profile_positive[8], int(pos_positive[8]),
#             force_profile_negative[0], int(pos_negative[0]),
#             force_profile_negative[1], int(pos_negative[1]),
#             force_profile_negative[2], int(pos_negative[2]),
#             force_profile_negative[3], int(pos_negative[3]),
#             force_profile_negative[4], int(pos_negative[4]),
#             force_profile_negative[5], int(pos_negative[5]),
#             force_profile_negative[6], int(pos_negative[6]),
#             force_profile_negative[7], int(pos_negative[7]),
#             force_profile_negative[8], int(pos_negative[8])
#         )

#     def _build_set_force_scale_factor_query(self, force_scale_factor, axis):
#         return struct.pack('<IIIH', 0xCE, axis, 0x20, force_scale_factor)

#     def _sendThenReceive(self, send_data):
#         self.sock.sendto(send_data, self.remoteEndpoint)
#         self.sock.recvfrom(8192)  # 接收响应，但不处理

#     # ===================== 对外接口 =====================
#     def set_force_profile(self, axis_name: str, positive_torque, negative_torque):
#     # """设置某个轴的 force profile (输入 Nm, 会自动转换)"""
#          axis = getattr(AxisBitmask, axis_name)

#          axis_k = {
#         "Elevator": 250 / 0.25,       # 手杆
#         "Aileron": 250 / 0.25,       # 手杆
#         "Rudder": 25 / 2.15          # 脚蹬
#                    }
#          k = axis_k.get(axis_name)
         
#          # 转换成 force_profile (整数)
#          force_profile_positive = [int(t * k) for t in positive_torque]
#          force_profile_negative = [int(t * k) for t in negative_torque]
         
#          # 每个轴的自定义 position
#          positions_config = {
#              "Elevator": {
#                  "positive": [i * 254 for i in range(1, 10)],
#                  "negative": [i * 241 for i in range(1, 10)]
#              },
#              "Aileron": {
#                  "positive": [i * 302 for i in range(1, 10)],
#                  "negative": [i * 312 for i in range(1, 10)]
#              },
#              "Rudder": {
#                  "positive": [i * 3800 for i in range(1, 10)],
#                  "negative": [i * 3800 for i in range(1, 10)]
#              },
# #             "Collective": {
# #                 "positive": [i * 250 for i in range(1, 10)],
# #                 "negative": [i * 250 for i in range(1, 10)]
# #             }
#          }
         
#          if axis_name in positions_config:
#              positions_p = positions_config[axis_name]["positive"]
#              positions_n = positions_config[axis_name]["negative"]
#          else:
#              # 默认均分
#              positions_p = [i * 250 for i in range(1, 10)]
#              positions_n = [i * 250 for i in range(1, 10)]
         
#          # 发送 profile
#          query = self._build_set_extended_force_profile_query(
#              force_profile_positive, positions_p,
#              force_profile_negative, positions_n,
#              axis
#          )
#          self._sendThenReceive(query)
#          print(f"[OK] {axis_name} force profile start")

#     def set_force_scale(self, axis_name: str, scale_value: int):
#        # """设置某个轴的缩放因子 (1~1000)"""
#         axis = getattr(AxisBitmask, axis_name)
#         query = self._build_set_force_scale_factor_query(scale_value, axis)
#         self._sendThenReceive(query)
#         print(f"[OK] {axis_name}already set {scale_value}")

#     def close(self):
#         self.sock.close()




from enum import IntEnum
import socket
import struct

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


class ForceProfileManager:
    def __init__(self, ip: str = "127.0.0.1", port: int = 15090, timeout: int = 8):
        self.remoteEndpoint = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
        self.sock.settimeout(timeout)
        self.sock.bind(('', 0))
        

    # ===================== UDP 命令构建 =====================
    def _build_set_extended_force_profile_query(self, force_profile_positive, pos_positive,
                                                force_profile_negative, pos_negative, axis):
        return struct.pack(
            '<III' + ('Hi' * 18),
            0xCE, axis, 0xE0,
            force_profile_positive[0], int(pos_positive[0]),
            force_profile_positive[1], int(pos_positive[1]),
            force_profile_positive[2], int(pos_positive[2]),
            force_profile_positive[3], int(pos_positive[3]),
            force_profile_positive[4], int(pos_positive[4]),
            force_profile_positive[5], int(pos_positive[5]),
            force_profile_positive[6], int(pos_positive[6]),
            force_profile_positive[7], int(pos_positive[7]),
            force_profile_positive[8], int(pos_positive[8]),
            force_profile_negative[0], int(pos_negative[0]),
            force_profile_negative[1], int(pos_negative[1]),
            force_profile_negative[2], int(pos_negative[2]),
            force_profile_negative[3], int(pos_negative[3]),
            force_profile_negative[4], int(pos_negative[4]),
            force_profile_negative[5], int(pos_negative[5]),
            force_profile_negative[6], int(pos_negative[6]),
            force_profile_negative[7], int(pos_negative[7]),
            force_profile_negative[8], int(pos_negative[8])
        )

    def _build_set_force_scale_factor_query(self, force_scale_factor, axis):
        return struct.pack('<IIIH', 0xCE, axis, 0x20, force_scale_factor)

    def _sendThenReceive(self, send_data):
        self.sock.sendto(send_data, self.remoteEndpoint)
        self.sock.recvfrom(8192)  # 接收响应，但不处理

    # ===================== 对外接口 =====================
    def set_force_profile(self, axis_name: str, positive_torque, negative_torque,
                          positions_positive, positions_negative):
        #"""
        #设置某个轴的 force profile (输入 Nm，会自动转换)
        #支持不同轴使用不同比例系数，并可手动传入 position
        #"""
        axis = getattr(AxisBitmask, axis_name)

        # 每个轴对应比例系数
        axis_k = {
            "Elevator": 250 / 0.15,  # 手杆
            "Aileron": 250 / 0.15,   # 手杆
            "Rudder": 25 / 2.25      # 脚蹬
        }
        k = axis_k.get(axis_name)

        # 转换 force profile 并裁剪 UInt16
        force_profile_positive = [max(0, min(65535, int(t * k))) for t in positive_torque]
        force_profile_negative = [max(0, min(65535, int(t * k))) for t in negative_torque]

        # # 使用用户传入的 position 或默认配置
        # if positions_positive is None or positions_negative is None:
        #     positions_config = {
        #         "Elevator": {
        #             "positive": [i * 254 for i in range(1, 10)],
        #             "negative": [i * 241 for i in range(1, 10)]
        #         },
        #         "Aileron": {
        #             "positive": [i * 302 for i in range(1, 10)],
        #             "negative": [i * 312 for i in range(1, 10)]
        #         },
        #         "Rudder": {
        #             "positive": [i * 3800 for i in range(1, 10)],
        #             "negative": [i * 3800 for i in range(1, 10)]
        #         }
        #     }
        #     if axis_name in positions_config:
        #         positions_p = positions_config[axis_name]["positive"]
        #         positions_n = positions_config[axis_name]["negative"]
        #     else:
        #         positions_p = [i * 250 for i in range(1, 10)]
        #         positions_n = [i * 250 for i in range(1, 10)]
        # else:
        positions_p = positions_positive
        positions_n = positions_negative

        # 发送 profile
        query = self._build_set_extended_force_profile_query(
            force_profile_positive, positions_p,
            force_profile_negative, positions_n,
            axis
        )
        self._sendThenReceive(query)
        #print(f"[OK] {axis_name} force profile start")

    def set_force_scale(self, axis_name: str, scale_value: int):
        #"""设置某个轴的缩放因子 (1~1000)"""
        axis = getattr(AxisBitmask, axis_name)
        query = self._build_set_force_scale_factor_query(scale_value, axis)
        self._sendThenReceive(query)
        #print(f"[OK] {axis_name} already set {scale_value}")

    def close(self):
        self.sock.close()
