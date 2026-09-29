# #!/usr/bin/env python3
# import socket
# import struct
# from enum import IntEnum
# import time

# HOST = "127.0.0.1"   # CLS2Sim IP
# PORT = 15090         # CLS2Sim UDP port

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.settimeout(2)

# # ==== Axis bitmask ====
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

# # Setting IDs
# SETTING_AUTOPILOT_FORCE    = 0x50
# SETTING_AUTOPILOT_SPEED    = 0x60
# SETTING_AUTOPILOT_ENABLE   = 0x70
# SETTING_AUTOPILOT_POSITION = 0x80

# def send_setting(axis, setting_id, value, fmt):
#     """Generic function to send a Settings Control command (0xCE)."""
#     packet = struct.pack("<Iii" + fmt,
#                          0xCE,        # Command
#                          axis,        # Axis bitmask
#                          setting_id,
#                          value)
#     sock.sendto(packet, (HOST, PORT))

# def prepare_axis(axis_mask):
#     """Prepare axis: set force, speed, and enable autopilot."""
#     send_setting(axis_mask, SETTING_AUTOPILOT_FORCE, 4500, "H")  # Force
#     send_setting(axis_mask, SETTING_AUTOPILOT_SPEED, 30, "H")    # Speed
#     send_setting(axis_mask, SETTING_AUTOPILOT_ENABLE, 1, "B")    # Enable

# def move_axis_to_position(axis_mask, position):
#     """Move given axis to a target position (-1.0 .. 1.0)."""
#     send_setting(axis_mask, SETTING_AUTOPILOT_POSITION, float(position), "f")

# def build_get_pos_query(axis_mask):
#     """Build GetData (0xD0) query for normalized position (0x11)."""
#     return struct.pack("<III", 0xD0, axis_mask, 0x11)

# def read_pos_classs():
#     """Request and parse normalized positions of Elevator and Aileron."""
#     axis_mask = AxisBitmask.Elevator | AxisBitmask.Aileron
#     query = build_get_pos_query(axis_mask)
#     sock.sendto(query, (HOST, PORT))
#     data, _ = sock.recvfrom(8192)

#     try:
#         length, status, node1, pos1, node2, pos2 = struct.unpack("<HI B f B f", data[:15])
#         return (node1, pos1, node2, pos2)
#     except Exception as e:
#         print("Failed to parse position response:", e)
#         return None

# def main():
#     prepare_axis(AxisBitmask.Elevator)
#     prepare_axis(AxisBitmask.Aileron)

#     print("Enter target positions for Elevator and Aileron (-1.0 .. 1.0).")
#     print("Example: 0.3 -0.5")
#     print("Press Ctrl+C to exit.")

#     while True:
#         try:
#             line = input("Elevator Aileron: ").strip()
#             if not line:
#                 continue
#             vals = line.split()
#             if len(vals) != 2:
#                 print("Please enter two numbers, e.g. 0.2 -0.4")
#                 continue

#             elevator_pos = float(vals[0])
#             aileron_pos  = float(vals[1])

#             if not -1.0 <= elevator_pos <= 1.0 or not -1.0 <= aileron_pos <= 1.0:
#                 print("Values must be between -1.0 and 1.0")
#                 continue

#             move_axis_to_position(AxisBitmask.Elevator, -elevator_pos)
#             move_axis_to_position(AxisBitmask.Aileron, -aileron_pos)

#             result = read_pos_classs()
#             if result:
#                 node1, pos1, node2, pos2 = result
#                 print(f"Current positions -> Node {node1}: {pos1:.2f}, Node {node2}: {pos2:.2f}")

#         except KeyboardInterrupt:
#             print("\nExiting.")
#             break
#         except Exception as e:
#             print("Error:", e)

# if __name__ == "__main__":
#     main()

# #!/usr/bin/env python3
# import socket
# import struct
# from enum import IntEnum

# HOST = "127.0.0.1"   # CLS2Sim IP
# PORT = 15090         # CLS2Sim UDP port

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.settimeout(2)

# # ==== Axis bitmask ====
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

# # ==== Setting IDs ====
# SETTING_AUTOPILOT_FORCE    = 0x50
# SETTING_AUTOPILOT_SPEED    = 0x60
# SETTING_AUTOPILOT_ENABLE   = 0x70
# SETTING_AUTOPILOT_POSITION = 0x80

# def send_setting(axis, setting_id, value, fmt):
#     """Generic function to send settings (Settings Control, 0xCE)."""
#     packet = struct.pack("<Iii" + fmt,
#                          0xCE,        # Command
#                          axis,        # Axis bitmask
#                          setting_id,
#                          value)
#     sock.sendto(packet, (HOST, PORT))

# def prepare_axis(axis_mask):
#     """Prepare axis: set force and speed, do not enable automatically."""
#     send_setting(axis_mask, SETTING_AUTOPILOT_FORCE, 4500, "H")  # Force
#     send_setting(axis_mask, SETTING_AUTOPILOT_SPEED, 30, "H")    # Speed

# def enable_pos_contr_class(axis_mask, enable: bool):
#     """Enable/disable position control (1=on, 0=off)."""
#     send_setting(axis_mask, SETTING_AUTOPILOT_ENABLE, 1 if enable else 0, "B")

# def move_axis_to_position(axis_mask, position):
#     """Move axis to position (-1.0 .. 1.0)."""
#     send_setting(axis_mask, SETTING_AUTOPILOT_POSITION, float(position), "f")

# def build_get_pos_query(axis_mask):
#     """Build query packet (GetData 0xD0, Normalized position 0x11)."""
#     return struct.pack("<III", 0xD0, axis_mask, 0x11)

# def read_pos_classs():
#     """Read current normalized position of Elevator + Aileron."""
#     axis_mask = AxisBitmask.Elevator | AxisBitmask.Aileron
#     query = build_get_pos_query(axis_mask)
#     sock.sendto(query, (HOST, PORT))
#     data, _ = sock.recvfrom(8192)

#     try:
#         length, status, node1, pos1, node2, pos2 = struct.unpack("<HI B f B f", data[:15])
#         return (node1, pos1, node2, pos2)
#     except Exception as e:
#         print("Failed to parse position response:", e)
#         return None

# def main():
#     prepare_axis(AxisBitmask.Elevator)
#     prepare_axis(AxisBitmask.Aileron)

#     print("Input 1 -> Enable position control, Input 0 -> Disable position control")
#     print("Input two values -> Control Elevator and Aileron target position (-1.0 .. 1.0)")
#     print("Example: 0.3 -0.5")
#     print("Press Ctrl+C to exit.")

#     while True:
#         try:
#             line = input("Enter command: ").strip()
#             if not line:
#                 continue

#             # === Enable/disable ===
#             if line == "1":
#                 enable_pos_contr_class(AxisBitmask.Elevator | AxisBitmask.Aileron, True)
#                 print("Position control enabled")
#                 continue
#             elif line == "0":
#                 enable_pos_contr_class(AxisBitmask.Elevator | AxisBitmask.Aileron, False)
#                 print("Position control disabled")
#                 continue

#             # === Two floats for positions ===
#             vals = line.split()
#             if len(vals) != 2:
#                 print("Enter two values or 1/0 for enable/disable")
#                 continue

#             elevator_pos = float(vals[0])
#             aileron_pos  = float(vals[1])

#             if not -1.0 <= elevator_pos <= 1.0 or not -1.0 <= aileron_pos <= 1.0:
#                 print("Values must be between -1.0 and 1.0")
#                 continue

#             move_axis_to_position(AxisBitmask.Elevator, -elevator_pos)
#             move_axis_to_position(AxisBitmask.Aileron, -aileron_pos)

#             result = read_pos_classs()
#             if result:
#                 node1, pos1, node2, pos2 = result
#                 print(f"Current axis positions -> Node {node1}: {pos1:.2f}, Node {node2}: {pos2:.2f}")

#         except KeyboardInterrupt:
#             print("\nProgram exited.")
#             break
#         except Exception as e:
#             print("Error:", e)

# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
import socket
import struct
from enum import IntEnum

HOST = "127.0.0.1"   # CLS2Sim IP
PORT = 15090         # CLS2Sim UDP port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)

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

# ==== Setting IDs ====
SETTING_AUTOPILOT_FORCE    = 0x50
SETTING_AUTOPILOT_SPEED    = 0x60
SETTING_AUTOPILOT_ENABLE   = 0x70
SETTING_AUTOPILOT_POSITION = 0x80

def send_setting(axis, setting_id, value, fmt):
    """Generic function to send settings (Settings Control, 0xCE)."""
    packet = struct.pack("<III" + fmt,
                         0xCE,        # Command
                         axis,        # Axis bitmask
                         setting_id,
                         value)
    sock.sendto(packet, (HOST, PORT))

def prepare_axis(axis_mask):
    """Prepare axis: set force and speed, do not enable automatically."""
    send_setting(axis_mask, SETTING_AUTOPILOT_FORCE, 5000, "H")  # Force
    send_setting(axis_mask, SETTING_AUTOPILOT_SPEED, 50, "H")    # Speed

def enable_pos_contr_class(axis_mask, enable: bool):
    """Enable/disable position control (1=on, 0=off)."""
    send_setting(axis_mask, SETTING_AUTOPILOT_ENABLE, 1 if enable else 0, "B")

def move_axis_to_position(axis_mask, position):
    """Move axis to position (-1.0 .. 1.0)."""
    send_setting(axis_mask, SETTING_AUTOPILOT_POSITION, float(position), "f")

def build_get_pos_query(axis_mask):
    """Build query packet (GetData 0xD0, Normalized position 0x11)."""
    return struct.pack("<III", 0xD0, axis_mask, 0x11)

def read_pos_classs():
    """Read current normalized position of Elevator + Aileron + Rudder."""
    axis_mask = AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder
    query = build_get_pos_query(axis_mask)
    sock.sendto(query, (HOST, PORT))
    data, _ = sock.recvfrom(8192)

    try:
        # 每个 axis 返回: B f (nodeID + pos)
        # 前面有 length (H), status (I)
        length, status = struct.unpack("<HI", data[:6])
        results = []
        offset = 6
        while offset + 5 <= len(data):  # 至少要有 1B + 4B
            node, pos = struct.unpack("<Bf", data[offset:offset+5])
            results.append((node, pos))
            offset += 5
        return results
    except Exception as e:
        print("Failed to parse position response:", e)
        return None

def main():
    prepare_axis(AxisBitmask.Elevator)
    prepare_axis(AxisBitmask.Aileron)
    prepare_axis(AxisBitmask.Rudder)

    print("Input 1 -> Enable position control, Input 0 -> Disable position control")
    print("Input three values -> Control Elevator, Aileron, Rudder (-1.0 .. 1.0)")
    print("Example: 0.3 -0.5 0.2")
    print("Press Ctrl+C to exit.")

    while True:
        try:
            line = input("Enter command: ").strip()
            if not line:
                continue

            # === Enable/disable ===
            if line == "1":
                enable_pos_contr_class(AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder, True)
                print("Position control enabled")
                continue
            elif line == "0":
                enable_pos_contr_class(AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder, False)
                print("Position control disabled")
                continue

            # === Three floats for positions ===
            vals = line.split()
            if len(vals) != 3:
                print("Enter three values or 1/0 for enable/disable")
                continue

            elevator_pos = float(vals[0])
            aileron_pos  = float(vals[1])
            rudder_pos   = float(vals[2])

            for val in (elevator_pos, aileron_pos, rudder_pos):
                if not -1.0 <= val <= 1.0:
                    print("Values must be between -1.0 and 1.0")
                    break
            else:
                move_axis_to_position(AxisBitmask.Elevator, -elevator_pos)
                move_axis_to_position(AxisBitmask.Aileron, -aileron_pos)
                move_axis_to_position(AxisBitmask.Rudder, rudder_pos)

                results = read_pos_classs()
                if results:
                    txt = " | ".join([f"Node {n}: {p:.2f}" for n, p in results])
                    print(f"Current axis positions -> {txt}")

        except KeyboardInterrupt:
            print("\nProgram exited.")
            break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
