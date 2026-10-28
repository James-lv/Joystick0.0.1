# #!/usr/bin/env python3
# import socket
# import struct
# from enum import IntEnum

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

# SETTING_AUTOPILOT_FORCE    = 0x50
# SETTING_AUTOPILOT_SPEED    = 0x60
# SETTING_AUTOPILOT_ENABLE   = 0x70
# SETTING_AUTOPILOT_POSITION = 0x80

# class PositionControl:
#     def __init__(self, host="127.0.0.1", port=15090):
#         self.HOST = host
#         self.PORT = port
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.sock.settimeout(2)
    
#     # ------------------- 核心功能 -------------------
#     def send_setting(self, axis, setting_id, value, fmt):
#         """Generic function to send settings (0xCE command)."""
#         packet = struct.pack("<Iii" + fmt, 0xCE, axis, setting_id, value)
#         self.sock.sendto(packet, (self.HOST, self.PORT))

#     def prepare_axis(self, axis_mask):
#         """Prepare axis: set force and speed, do not enable automatically."""
#         self.send_setting(axis_mask, SETTING_AUTOPILOT_FORCE, 4500, "H")
#         self.send_setting(axis_mask, SETTING_AUTOPILOT_SPEED, 30, "H")

#     def enable_pos_contr_class(self, axis_mask, enable: bool):
#         """Enable/disable position control."""
#         self.send_setting(axis_mask, SETTING_AUTOPILOT_ENABLE, 1 if enable else 0, "B")

#     def move_axis_to_position(self, axis_mask, position):
#         """Move axis to position (-1.0 .. 1.0)."""
#         self.send_setting(axis_mask, SETTING_AUTOPILOT_POSITION, float(position), "f")

#     def build_get_pos_query(self, axis_mask):
#         """Build query packet for current position."""
#         return struct.pack("<III", 0xD0, axis_mask, 0x11)

#     def read_pos_classs(self):
#         """Read current normalized position of Elevator + Aileron."""
#         axis_mask = AxisBitmask.Elevator | AxisBitmask.Aileron
#         query = self.build_get_pos_query(axis_mask)
#         self.sock.sendto(query, (self.HOST, self.PORT))
#         try:
#             data, _ = self.sock.recvfrom(8192)
#             length, status, node1, pos1, node2, pos2 = struct.unpack("<HI B f B f", data[:15])
#             return (node1, pos1, node2, pos2)
#         except Exception as e:
#             print("Failed to parse position response:", e)
#             return None

#     # ------------------- 高级接口 -------------------
#     def set_target_positions(self, elevator_pos, aileron_pos):
#         """Set Elevator and Aileron positions (-1.0..1.0)."""
#         self.move_axis_to_position(AxisBitmask.Elevator, -elevator_pos)
#         self.move_axis_to_position(AxisBitmask.Aileron, -aileron_pos)
#         return self.read_pos_classs()

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

SETTING_AUTOPILOT_FORCE    = 0x50
SETTING_AUTOPILOT_SPEED    = 0x60
SETTING_AUTOPILOT_ENABLE   = 0x70
SETTING_AUTOPILOT_POSITION = 0x80

class PositionController:
    def __init__(self, host="127.0.0.1", port=15090):
        self.HOST = host
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(2)

    # ------------------- 核心功能 -------------------
    def send_setting(self, axis, setting_id, value, fmt):
        """Send a generic 0xCE command."""
        packet = struct.pack("<III" + fmt,
                             0xCE, axis, setting_id, value)
        self.sock.sendto(packet, (self.HOST, self.PORT))

    def prepare_axis(self, axis_mask):
        """Prepare axis with force and speed."""
        self.send_setting(axis_mask, SETTING_AUTOPILOT_FORCE, 5000, "H")
        self.send_setting(axis_mask, SETTING_AUTOPILOT_SPEED, 50, "H")

    def enable_position_control(self, axis_mask, enable: bool):
        """Enable or disable position control."""
        self.send_setting(axis_mask, SETTING_AUTOPILOT_ENABLE, 1 if enable else 0, "B")

    def move_axis_to_position(self, axis_mask, position):
        """Move axis to a normalized position (-1.0..1.0)."""
        self.send_setting(axis_mask, SETTING_AUTOPILOT_POSITION, float(position), "f")

    def build_get_pos_query(self, axis_mask):
        """Build a position query packet."""
        return struct.pack("<III", 0xD0, axis_mask, 0x11)

    def read_positions(self, axis_mask=AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder):
        """Read normalized positions of specified axes."""
        query = self.build_get_pos_query(axis_mask)
        self.sock.sendto(query, (self.HOST, self.PORT))
        try:
            data, _ = self.sock.recvfrom(8192)
            length, status = struct.unpack("<HI", data[:6])
            results = []
            offset = 6
            while offset + 5 <= len(data):
                node, pos = struct.unpack("<Bf", data[offset:offset+5])
                results.append((node, pos))
                offset += 5
            return results
        except Exception as e:
            print("Failed to parse position response:", e)
            return None

    # ------------------- 高级接口 -------------------
    def set_target_positions(self, elevator, aileron, rudder):
        """Set positions for Elevator, Aileron, Rudder."""
        self.move_axis_to_position(AxisBitmask.Elevator, -elevator)
        self.move_axis_to_position(AxisBitmask.Aileron, -aileron)
        self.move_axis_to_position(AxisBitmask.Rudder, rudder)
        return self.read_positions()

    # ------------------- 命令行交互 -------------------
    def interactive_control(self):
        """Interactive loop for position control."""
        # 准备轴
        for axis in (AxisBitmask.Elevator, AxisBitmask.Aileron, AxisBitmask.Rudder):
            self.prepare_axis(axis)

        print("Input 1 -> Enable position control, Input 0 -> Disable position control")
        print("Input three values -> Control Elevator, Aileron, Rudder (-1.0 .. 1.0)")
        print("Example: 0.3 -0.5 0.2")
        print("Press Ctrl+C to exit.")

        while True:
            try:
                line = input("Enter command: ").strip()
                if not line:
                    continue

                if line == "1":
                    self.enable_position_control(AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder, True)
                    print("Position control enabled")
                    continue
                elif line == "0":
                    self.enable_position_control(AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder, False)
                    print("Position control disabled")
                    continue

                vals = line.split()
                if len(vals) != 3:
                    print("Enter three values or 1/0 for enable/disable")
                    continue

                elevator, aileron, rudder = map(float, vals)
                if not all(-1.0 <= v <= 1.0 for v in (elevator, aileron, rudder)):
                    print("Values must be between -1.0 and 1.0")
                    continue

                self.set_target_positions(elevator, aileron, rudder)
                results = self.read_positions()
                if results:
                    txt = " | ".join([f"Node {n}: {p:.2f}" for n, p in results])
                    print(f"Current axis positions -> {txt}")

            except KeyboardInterrupt:
                print("\nProgram exited.")
                break
            except Exception as e:
                print("Error:", e)