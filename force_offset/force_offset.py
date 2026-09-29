# #!/usr/bin/env python3

# import socket
# import struct


# # Protocol for commands is as documented in https://cls2sim.brunner-innovation.swiss/

# def main():
#     timeout = 8
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
#     sock.settimeout(timeout)
#     sock.bind(('', 0))

#     remoteEndpoint = ('127.0.0.1', 15090)

#     # OverrideCOmmand, Elevator and Aileron Axis, VibrationOverride
#     # necessary so you are allowed to control force externally
#     query_setvibrationoverride = struct.pack('<III', 0xD1, 0x3, 0x5)

#     # Command GetData(0xD0), For axes 0x1 and 0x2 (pitch,roll) (= 0x3) and read pos as float (dataid 0x11)
#     query_readpos = struct.pack('<III', 0xD0, 0x3, 0x11)

#     # after each send you MUST do a read, even if you don't do anything with the reponse
#     sock.sendto(query_setvibrationoverride, remoteEndpoint)
#     response, address = sock.recvfrom(8192)

#     while True:
#         sock.sendto(query_readpos, remoteEndpoint)
#         response, address = sock.recvfrom(8192)

#         length, status, node_pitch, pos_pitch, node_roll, pos_roll = struct.unpack('<HBHfHf', response)

#         # raw force value is in internal units. if you want to know how many N or Nm you would need to measure.
#         # In CLS2SIm, create a new profile, then go to axis forces settings.
#         # Open force settings for pitch, in the force diagram dialog uncheck 'profile mode'.
#         # Set first force value of the diagram as low as possible, so long as it does not start to oscillate. (50 in internal units should be good)
#         # Repeat for roll axis.
#         #
#         # Now you should be able to change calculations below to generate your own force
#         pitch_force_raw = (int)(10000 * pos_pitch) * -1
#         roll_force_raw = (int)(2000 * pos_roll) * -1

#         print(roll_force_raw)

#         # SetSettings Command, Axis Elevator, SetForceOffset, force
#         query_setforce_pitch = struct.pack('<IIIi', 0xCE, 0x1, 0xD0, pitch_force_raw)

#         # SetSettings Command, Axis Aileron, SetForceOffset, force
#         query_setforce_roll = struct.pack('<IIIi', 0xCE, 0x2, 0xD0, roll_force_raw)

#         sock.sendto(query_setforce_pitch, remoteEndpoint)
#         response, address = sock.recvfrom(8192)
#         sock.sendto(query_setforce_roll, remoteEndpoint)
#         response, address = sock.recvfrom(8192)

#     sock.close()


# if __name__ == "__main__":
#     main()



# #!/usr/bin/env python3
# import time
# import struct
# import socket


# def calc_force(pos: float, k: int) -> int:
#     #"""
#     #非线性力模型: F = -k * pos * |pos|
#     #- pos: 位置 (float, 通常在 [-1,1] 或更大范围)
#     #- k: 力系数
#     #"""
#     return int(-k * pos * abs(pos))


# def main():
#     timeout = 8
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
#     sock.settimeout(timeout)
#     sock.bind(('', 0))

#     remoteEndpoint = ('127.0.0.1', 15090)

#     # === 开启外部控制 ===
#     query_setvibrationoverride = struct.pack('<III', 0xD1, 0x3, 0x5)
#     sock.sendto(query_setvibrationoverride, remoteEndpoint)
#     response, address = sock.recvfrom(8192)
#     print("Override response:", response.hex())

#     # === 读取 pitch & roll 位置 ===
#     query_readpos = struct.pack('<III', 0xD0, 0x3, 0x11)

#     # 力系数，可自行调节
#     k_pitch = 5000
#     k_roll = 100

#     try:
#         while True:
#             # === 1. 获取位置 ===
#             sock.sendto(query_readpos, remoteEndpoint)
#             response, address = sock.recvfrom(8192)

#             if len(response) < 15:
#                 print("Unexpected response length:", len(response))
#                 continue

#             try:
#                 length, status, node_pitch, pos_pitch, node_roll, pos_roll = \
#                     struct.unpack('<HBHfHf', response[:15])
#             except Exception as e:
#                 print("Unpack error:", e, response.hex())
#                 continue

#             # === 2. 计算非线性力 ===
#             pitch_force_raw = calc_force(pos_pitch, k_pitch)
#             roll_force_raw = calc_force(pos_roll, k_roll)

#             print(f"Pitch pos={pos_pitch:.3f}, force={pitch_force_raw} | "
#                   f"Roll pos={pos_roll:.3f}, force={roll_force_raw}")

#             # === 3. 发 Pitch 力 ===
#             query_setforce_pitch = struct.pack('<IIIi', 0xCE, 0x1, 0xD0, pitch_force_raw)
#             sock.sendto(query_setforce_pitch, remoteEndpoint)
#             try:
#                 response, address = sock.recvfrom(8192)
#                 # print("Pitch response:", response.hex())
#             except socket.timeout:
#                 print("Pitch response timeout")

#             time.sleep(0.01)

#             # === 4. 发 Roll 力 ===
#             query_setforce_roll = struct.pack('<IIIi', 0xCE, 0x2, 0xD0, roll_force_raw)
#             sock.sendto(query_setforce_roll, remoteEndpoint)
#             try:
#                 response, address = sock.recvfrom(8192)
#                 # print("Roll response:", response.hex())
#             except socket.timeout:
#                 print("Roll response timeout")

#             time.sleep(0.01)

#     except ConnectionResetError as e:
#         print("Connection reset by CLS2Sim:", e)

#     except KeyboardInterrupt:
#         print("Interrupted by user")

#     finally:
#         sock.close()
#         print("Socket closed.")


# if __name__ == "__main__":
#     main()
