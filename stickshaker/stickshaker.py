# import socket
# import struct

# def main():
#     timeout = 100
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
#     sock.settimeout(timeout)
#     sock.bind(('', 0))

#     remoteEndpoint = ('127.0.0.1', 15090)

#     # 开启外部控制权限 (Override)
#     query_setvibration_override = struct.pack('<III', 0xD1, 0x3, 0x5)
#     sock.sendto(query_setvibration_override, remoteEndpoint)
#     response, address = sock.recvfrom(8192)

#     # 设置振动参数
#     force = 50
#     freq = 100
#     interval_100qs_units = freq*10
#     query_setvibration_speed_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC1, interval_100qs_units)
#     query_setvibration_force_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC2, force)

#     sock.sendto(query_setvibration_speed_fast, remoteEndpoint)
#     response, address = sock.recvfrom(8192)

#     sock.sendto(query_setvibration_force_fast, remoteEndpoint)
#     response, address = sock.recvfrom(8192)

#     # 预定义 enable/disable 指令
#     query_setvibration_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 1)
#     query_setvibration_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 0)

#     print("输入 1 = 启用振动，0 = 停止振动，q = 退出")

#     while True:
#         cmd = input("请输入指令: ").strip()
#         try:
#             if cmd == "1":
#                 sock.sendto(query_setvibration_enable, remoteEndpoint)
#                 response, address = sock.recvfrom(8192)
#                 print("✅ 振动已启用")
#             elif cmd == "0":
#                 sock.sendto(query_setvibration_disable, remoteEndpoint)
#                 response, address = sock.recvfrom(8192)
#                 print("⏹️ 振动已关闭")
#             elif cmd.lower() == "q":
#                 print("程序退出")
#                 break
#             else:
#                 print("无效输入，请输入 1 / 0 / q")
#         except Exception as e:
#             print(f"错误: {e}")
#             break

#     sock.close()

# if __name__ == "__main__":
#     main()

# import socket
# import struct

# def main():
#     timeout = 100
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
#     sock.settimeout(timeout)
#     sock.bind(('', 0))

#     remoteEndpoint = ('127.0.0.1', 15090)

#     # 开启外部控制权限 (Override)
#     query_setvibration_override = struct.pack('<III', 0xD1, 0x3, 0x5)
#     sock.sendto(query_setvibration_override, remoteEndpoint)
#     response, address = sock.recvfrom(8192)

#     # 初始化 force 和 freq
#     force = 50
#     freq = 100

#     def send_vibration(force_val, freq_val):
#         interval_100qs_units = freq_val * 10
#         query_setvibration_speed_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC1, interval_100qs_units)
#         query_setvibration_force_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC2, force_val)
#         sock.sendto(query_setvibration_speed_fast, remoteEndpoint)
#         sock.recvfrom(8192)
#         sock.sendto(query_setvibration_force_fast, remoteEndpoint)
#         sock.recvfrom(8192)

#     # 预定义 enable/disable 指令
#     query_setvibration_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 1)
#     query_setvibration_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 0)

#     print("指令说明:")
#     print("1 = 启用振动")
#     print("0 = 停止振动")
#     print("force=<值> 设置振动力度 0-100")
#     print("freq=<值> 设置振动频率 ms")
#     print("q = 退出程序")

#     while True:
#         cmd = input("请输入指令: ").strip()
#         try:
#             if cmd == "1":
#                 sock.sendto(query_setvibration_enable, remoteEndpoint)
#                 sock.recvfrom(8192)
#                 print("✅ 振动已启用")
#             elif cmd == "0":
#                 sock.sendto(query_setvibration_disable, remoteEndpoint)
#                 sock.recvfrom(8192)
#                 print("⏹️ 振动已关闭")
#             elif cmd.lower() == "q":
#                 print("程序退出")
#                 break
#             elif cmd.startswith("force="):
#                 try:
#                     force = int(cmd.split("=")[1])
#                     send_vibration(force, freq)
#                     print(f"💪 振动力度已设置为 {force}")
#                 except ValueError:
#                     print("⚠️ force 输入无效，请输入整数")
#             elif cmd.startswith("freq="):
#                 try:
#                     freq = int(cmd.split("=")[1])
#                     send_vibration(force, freq)
#                     print(f"🎵 频率已设置为 {freq} Hz")
#                 except ValueError:
#                     print("⚠️ freq 输入无效，请输入整数")
#             else:
#                 print("无效输入，请按说明操作")
#         except Exception as e:
#             print(f"错误: {e}")
#             break

#     sock.close()

# if __name__ == "__main__":
#     main()


import socket
import struct
import sys

def main():
    timeout = 100
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 5)
    sock.settimeout(timeout)
    sock.bind(('', 0))

    remoteEndpoint = ('127.0.0.1', 15090)

    # 开启外部控制权限 (Override)
    query_setvibration_override = struct.pack('<III', 0xD1, 0x3, 0x5)
    sock.sendto(query_setvibration_override, remoteEndpoint)
    sock.recvfrom(8192)

    # 默认 force 和 freq
    force = 50
    freq = 100
    vibration_enabled = False

    def send_vibration(force_val, freq_val):
        interval_100qs_units = freq_val * 10
        query_setvibration_speed_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC1, interval_100qs_units)
        query_setvibration_force_fast = struct.pack('<IIII', 0xCE, 0x1, 0xC2, force_val)
        sock.sendto(query_setvibration_speed_fast, remoteEndpoint)
        sock.recvfrom(8192)
        sock.sendto(query_setvibration_force_fast, remoteEndpoint)
        sock.recvfrom(8192)

    # 预定义 enable/disable 指令
    query_setvibration_enable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 1)
    query_setvibration_disable = struct.pack('<IIIB', 0xCE, 0x1, 0xC0, 0)

    print("输入 1=使能 0=停止 q=退出")
    print("输入 force freq 来同时修改，例如: 80 200")
    print("单个数字将按大小自动修改 force (≤100) 或 freq (>100)\n")

    while True:
        # 显示当前状态在同一行
        status = f"[{'ON ' if vibration_enabled else 'OFF'}] force={force}  freq={freq}  > "
        print(f"\r{status}", end='', flush=True)

        cmd = input().strip()
        try:
            if cmd == "1":
                sock.sendto(query_setvibration_enable, remoteEndpoint)
                sock.recvfrom(8192)
                vibration_enabled = True
            elif cmd == "0":
                sock.sendto(query_setvibration_disable, remoteEndpoint)
                sock.recvfrom(8192)
                vibration_enabled = False
            elif cmd.lower() == "q":
                print("\n程序退出")
                break
            else:
                # 尝试解析输入数字
                parts = cmd.replace(',', ' ').split()
                nums = [int(p) for p in parts if p.isdigit()]
                if not nums:
                    print("\n⚠️ 输入无效")
                    continue
                if len(nums) == 1:
                    val = nums[0]
                    if val <= 100:
                        force = val
                    else:
                        freq = val
                else:
                    # 同时修改 force 和 freq
                    force, freq = nums[0], nums[1]
                if vibration_enabled:
                    send_vibration(force, freq)
        except Exception as e:
            print(f"\n错误: {e}")
            break

    sock.close()

if __name__ == "__main__":
    main()
