
#!/usr/bin/env python3
import os
import sys
import json
import socket
import threading
import time
import subprocess
import ctypes
from ctypes import wintypes
import struct
import select
from enum import IntEnum
# ===================== CLS2Sim 关闭控制（捕获窗口关闭事件） =====================
try:
    import win32api
except ImportError:
    win32api = None

# ===================== 导入类文件 =====================

from pitch_signal_generator import PitchSignalGenerator
from postioncontrol import PositionControl 
from read_button_class import ButtonReader
from read_pos_class import PositionReader
from read_force import ForceReader
from brake import BrakeReader
from friction_class import FrictionController
from set_damping import dampController
from stickshake import stickshakercon
from External_force_profile import ForceProfileManager
from pos_to_editjoystick import PosReader_raw
from Axis_range_limits import AxisRangeController
from postion_window import positionwindow
from spring_force import PMoveBackController
from target_torque import TargetTorqueController
from trim_position import TrimController  # 新增 TrimController
from force_offset  import ForceOffsetController
from pitch_signal_generator import PitchSignalGenerator
# ===================== 配置文件 =====================
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "udpconfig.json")

if not os.path.exists(CONFIG_PATH):
    print("[ERROR] Config file not found!")
    sys.exit(1)
else:
    print("Config file found")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

UDP_IP             = cfg["UDP_IP"]
UDP_PORT           = cfg["UDP_PORT"]
HOST_IP            = cfg["HOST_IP"]
HOST_PORT          = cfg["HOST_PORT"]
UDP_IP_EJ          = cfg["UDP_IP_EJ"]
UDP_PORT_EJ        = cfg["UDP_PORT_EJ"]
edit_joystick_IP   = cfg["e_j_IP"]
edit_joystick_PORT = cfg["e_j_PORT"]
CLS2SIM_PATH       = cfg.get("CLS2SIM_PATH")
shake_cfg          = cfg.get("shake_control", {})
force_profile_cfg  = cfg.get("force_profile", {})
scaling_cfg        = cfg.get("scaling", {})
friction_cfg       = cfg.get("friction", {})
damp_cfg           = cfg.get("damp", {})    
Axlimit_cfg        = cfg.get("AxisRange", {})    
poswin_cfg         = cfg.get("poswin", {})
spring_cfg         = cfg.get("spring", {})
tartorque_cfg      = cfg.get("targettorqure", {})
forceoffset_cfg    = cfg.get("forceoffset", {})

FREQ               = cfg.get("send_frequency", 50)
T                  = 1.0 / FREQ

# ===================== CLS2Sim 最小化窗口 =====================
user32 = ctypes.WinDLL('user32', use_last_error=True)
SW_MINIMIZE = 6
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
GetWindowTextW = user32.GetWindowTextW
GetWindowTextLengthW = user32.GetWindowTextLengthW
ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
ShowWindow.restype = wintypes.BOOL

def find_window_partial(title_substr: str):
    hwnd_found = None
    def enum_proc(hwnd, lParam):
        nonlocal hwnd_found
        length = GetWindowTextLengthW(hwnd)
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            GetWindowTextW(hwnd, buffer, length + 1)
            if title_substr.lower() in buffer.value.lower():
                hwnd_found = hwnd
                return False
        return True
    EnumWindows(EnumWindowsProc(enum_proc), 0)
    return hwnd_found

def minimize_cls2sim():
    hwnd = find_window_partial("CLS2Sim")
    if hwnd:
        ShowWindow(hwnd, SW_MINIMIZE)
        print("[INFO] CLS2Sim minimized")
    else:
        print("[WARN] CLS2Sim window not found")

# ===================== 启动 CLS2Sim =====================
try:
    cls2sim_proc = subprocess.Popen([CLS2SIM_PATH], shell=False)
    time.sleep(25)
    minimize_cls2sim()
except Exception as e:
    print(f"[ERROR] CLS2Sim start failure: {e}")
    cls2sim_proc = None

# ===================== 捕获控制台关闭事件 =====================
def console_ctrl_handler(ctrl_type):
    print(f"[INFO] Console exit detected: {ctrl_type}")
    if cls2sim_proc and cls2sim_proc.poll() is None:
        print("[INFO] Closing CLS2Sim...")
        cls2sim_proc.terminate()
    return False

if win32api:
    win32api.SetConsoleCtrlHandler(console_ctrl_handler, True)

# ===================== AXIS =====================
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

# ===================== 初始化 joystick / force 模块 =====================\
pos_contr                =   PositionControl()
button_reader            =   ButtonReader()
position_reader          =   PositionReader()
force_reader             =   ForceReader()
brake_reader             =   BrakeReader()
stickshaker              =   stickshakercon()
force_manager            =   ForceProfileManager()
pos_reader_raw           =   PosReader_raw()
friction_ctrl            =   FrictionController()
damp_ctrl                =   dampController()
axlim_ctrl               =   AxisRangeController()
poswin_ctrl              =   positionwindow()
spring_ctrl              =   PMoveBackController()
tartorque_ctrl           =   TargetTorqueController()
forceoffset_ctrl         =   ForceOffsetController()
trim_controller          =   TrimController() 
pitch_signal_generator   =   PitchSignalGenerator()

# 准备位置控制轴
for axis in [AxisBitmask.Elevator, AxisBitmask.Aileron, AxisBitmask.Rudder]:
    pos_contr.prepare_axis(axis)

#stickshaker.set_force(200, 10)


# ===================== 初始化 Force Profile / Scaling / Friction =====================
for axis_name in ["Elevator", "Aileron", "Rudder"]:
    pos_values = force_profile_cfg.get(f"{axis_name}_positive", [0.0]*9)
    neg_values = force_profile_cfg.get(f"{axis_name}_negative", [0.0]*9)
    pos_positions = force_profile_cfg.get(f"{axis_name}_pos_position", [i*250 for i in range(1,10)])
    neg_positions = force_profile_cfg.get(f"{axis_name}_neg_position", [i*250 for i in range(1,10)])
    force_manager.set_force_profile(axis_name, pos_values, neg_values, pos_positions, neg_positions)

    scale_val = int(scaling_cfg.get(axis_name, 100))
    force_manager.set_force_scale(axis_name, scale_val)

    friction_val = float(friction_cfg.get(axis_name, 0.1))
    friction_ctrl.set_friction(axis_name, friction_val)

    damp_val = damp_cfg.get(axis_name, [1,4])
    damp_ctrl.set_damp(axis_name, damp_val)

    axrange_val = Axlimit_cfg.get(axis_name, [1,40])
    axlim_ctrl.set_axis_range(axis_name, axrange_val)
 
    #response = axlim_ctrl.set_axis_range(axis_name, axrange_val)
    #print(f"[AxisRange] {axis_name} -> [{axrange_val[0]}, {axrange_val[1]}] -> response: {response}")

    poswin_val = poswin_cfg.get(axis_name, 50)
    poswin_ctrl.set_poswin(axis_name, poswin_val)

    spring_val = spring_cfg.get(axis_name, 140)
    spring_ctrl.set_pmoveback(axis_name, spring_val)

    tartorque_val = tartorque_cfg.get(axis_name, 120)
    tartorque_ctrl.set_target_torque(axis_name, tartorque_val)

    forceoffset_val = forceoffset_cfg.get(axis_name,900)
    forceoffset_ctrl.set_force_offset(axis_name, forceoffset_val)

print("Force Profile, Scaling & Friction Initialized")


################气动力补偿用###################
FO_ele = forceoffset_cfg.get('Elevator', 910)#
FO_ail = forceoffset_cfg.get('Aileron', 0)  #
FO_rud = forceoffset_cfg.get('Rudder', 0)  #
############################################

# ===================== 全局状态 =====================
class GlobalState:
    offsets = None   # (ele, force_p, ail, force_r, rud, force_y)
    x = 3
    w = 1*x
    v = 1
    
#===============================================================
# ===================== UDP 接收主机控制 (位置 + 抖杆 +气动力+ Trim) =====================
# ===================== UDP 接收主机控制 (位置 + 抖杆 +气动力+ Trim) =====================
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# 关键优化
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
sock.setblocking(False)

send_enable = True
prev_pos_enable = 0
last_shake_enable = 0
last_pos_enable = 0      # 新增
last_trim_enable = 0     # 新增
last_ARJ21_K8 = 0        # 新增


def udp_listener():
    global send_enable, prev_pos_enable
    global last_shake_enable, last_pos_enable, last_trim_enable, last_ARJ21_K8  # 新增
    ramp_steps = 10
    ramp_dt = 0.01
    error_printed = False

    while True:  
               try:
                    data = None
                    rlist, _, _ = select.select([sock], [], [], 0.001)  # 超时时间 1ms
                    if rlist:
                        data, addr = sock.recvfrom(8192)
                    
                        # 如果缓冲区里还有旧数据，丢掉只保留最新一帧
                        while True:
                            rlist2, _, _ = select.select([sock], [], [], 0)
                            if rlist2:
                                data, addr = sock.recvfrom(8192)
                            else:
                               break

                    # --- 新结构: ---
                    if data is not None and len(data) >= 60:
                        pos_enable, shake_enable, trim_enable, ARJ21_K8, elevator, aileron, rudder, shake_force_in, shake_freq_in, trim_elevator, trim_aileron, trim_rudder, aerox, aeroy, aeroz = struct.unpack("<iiii8f3i", data[:60])
                    
                    
                    stickshaker.set_force(shake_force_in, shake_freq_in)
                    # ===== 抖杆控制 (边沿触发) =====
                    if shake_enable != last_shake_enable:  
                        if shake_enable == 1:
                            stickshaker.enable()
                        elif shake_enable == 0:
                            stickshaker.disable()
                        last_shake_enable = shake_enable
                    
                    # ===== 位置控制 (边沿触发) =====
                    if pos_enable != last_pos_enable:
                        if pos_enable == 1:
                            pos_contr.enable_pos_contr_class(AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder, pos_enable)
                            # 限幅[-1, 1]
                            e_cmd = max(min(elevator, 1.0), -1.0)
                            a_cmd = max(min(aileron,  1.0), -1.0)
                            r_cmd = max(min(rudder,   1.0), -1.0)
                            pos_contr.set_target_positions(e_cmd, a_cmd, r_cmd)
                        elif pos_enable == 0:
                            pos_contr.enable_pos_contr_class(AxisBitmask.Elevator | AxisBitmask.Aileron | AxisBitmask.Rudder, pos_enable)
                            pos_contr.set_target_positions(0.0, 0.0, 0.0)
                        last_pos_enable = pos_enable
                    else:
                        # enable未变化，但位置指令持续更新
                        if pos_enable == 1:
                            e_cmd = max(min(elevator, 1.0), -1.0)
                            a_cmd = max(min(aileron,  1.0), -1.0)
                            r_cmd = max(min(rudder,   1.0), -1.0)
                            pos_contr.set_target_positions(e_cmd, a_cmd, r_cmd)
                    
                    # ===== 配平控制 (边沿触发) =====
                    if trim_enable != last_trim_enable:
                        if trim_enable == 1:
                            try:
                                trim_dict = {
                                    AxisBitmask.Elevator : trim_elevator,
                                    AxisBitmask.Aileron  : trim_aileron,
                                    AxisBitmask.Rudder   : trim_rudder
                                }
                                trim_controller.set_multiple_trim_positions(trim_dict)
                            except Exception as e:
                                print(f"[Trim ERROR] {e}")
                        last_trim_enable = trim_enable
                    else:
                        # enable未变化，但配平值持续更新
                        if trim_enable == 1:
                            try:
                                trim_dict = {
                                    AxisBitmask.Elevator : trim_elevator,
                                    AxisBitmask.Aileron  : trim_aileron,
                                    AxisBitmask.Rudder   : trim_rudder
                                }
                                trim_controller.set_multiple_trim_positions(trim_dict)
                            except Exception as e:
                                print(f"[Trim ERROR] {e}")
                    
                    # ===== 气动力控制 (边沿触发) =====
                    if ARJ21_K8 != last_ARJ21_K8:
                        if ARJ21_K8 == 0:
                            try:
                                for axis_name in ["Elevator", "Aileron", "Rudder"]:
                                    scale = int(scaling_cfg.get(axis_name, 100))
                                    force_manager.set_force_scale(axis_name, scale)
                                    friction_val = float(friction_cfg.get(axis_name, 0.1))
                                    friction_ctrl.set_friction(axis_name, friction_val)
                                    spring_val = spring_cfg.get(axis_name, 140)
                                    spring_ctrl.set_pmoveback(axis_name, spring_val)
                                    damp_val = damp_cfg.get(axis_name, [1, 4])
                                    damp_ctrl.set_damp(axis_name, damp_val)
                            except Exception as e:
                                print(f"[Force Offset ERROR] {e}")
                        elif ARJ21_K8 == 1:
                            try:
                                #force_manager.set_force_scale("Elevator", 50)
                                #force_manager.set_force_scale("Rudder", 20)
                                damp_ctrl.set_damp("Elevator", [1, 10])
                                spring_ctrl.set_pmoveback("Elevator", 280)
                                friction_ctrl.set_friction("Elevator", 0.05)
                                damp_ctrl.set_damp("Rudder", [1, 10])
                                friction_ctrl.set_friction("Rudder", 5)
                            except Exception as e:
                                print(f"[Force Offset ERROR] {e}")
                        last_ARJ21_K8 = ARJ21_K8
                    
                    # ===== 气动力偏置 (每帧持续更新) =====
                    try:
                        if ARJ21_K8 == 0:
                            areo_dict = {
                                AxisBitmask.Elevator.name : FO_ele + aerox,
                                AxisBitmask.Aileron.name  : FO_ail + aeroy,
                                AxisBitmask.Rudder.name   : FO_rud + aeroz
                            }
                        elif ARJ21_K8 == 1:
                            force_manager.set_force_scale("Elevator", 5 + abs(aerox) * 65 / 3000)
                            force_manager.set_force_scale("Rudder",  10 + abs(aeroz) * 40 / 1500)
                            areo_dict = {
                                AxisBitmask.Elevator.name : FO_ele + aerox,
                                AxisBitmask.Aileron.name  : FO_ail + aeroy,
                                AxisBitmask.Rudder.name   : FO_ail + aeroz
                            }
                        forceoffset_ctrl.set_multiple_areo(areo_dict)
                    except Exception as e:
                        print(f"[Force Offset ERROR] {e}")
                    
                        prev_pos_enable = pos_enable

               except Exception as e:
                  if not error_printed:
                     print(f"[UDP ERROR] {e}")
                     error_printed = True
                  continue

threading.Thread(target=udp_listener, daemon=True).start()
#////////////////////////////////////////////////////////////////////////////////

# ===================== UDP 接收 人机 ==========================
def udp_force_profile_listener_bin():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP_EJ, UDP_PORT_EJ))
   # print(f"[INFO] Listening Force Profile UDP (binary) on port {edit_joystick_PORT}")

    AXIS_MAP = {1: "Elevator", 2: "Aileron", 3: "Rudder"}
    TORQUE_LIMITS = {"Elevator": 6.7, "Aileron": 6.7, "Rudder": 130.0}
     
    AXIS_FACTORS = {
        "Elevator": {"k": 1 / 0.0092,   "m": 0.025, "friction_factor": 0.025},
        "Aileron":  {"k": 1 / 0.0092, "m": 0.04, "friction_factor": 0.0225},
        "Rudder":   {"k": 228,        "m": 1,    "friction_factor": 0.013},
    }
    
    while True:
        try:
            # 更新 fmt 格式字符串
            fmt = "<B b B b 9f 9f 9f 9f i f i i i i f f i"
            expected_len = struct.calcsize(fmt)

            data, addr = udp_sock.recvfrom(8192)
            if len(data) < expected_len:
                print(f"[WARN] Data length too short: {len(data)}")
                continue

            unpacked = struct.unpack(fmt, data[:expected_len])
            #print("packet_in:", data.hex())

            axis_id = unpacked[1]
            axis_name = AXIS_MAP.get(axis_id)
            if not axis_name:
                print(f"[WARN] Unknown axis_id: {axis_id}")
                continue


            ######################################################
            factors = AXIS_FACTORS[axis_name]                    #
            k = factors["k"]                                     #
            if axis_name == "Elevator":                          #
                m = factors["m"] * 3                             #
            else:                                                #
                m = factors["m"]                                 #
            if axis_name == "Elevator":                          #
               friction_factor = factors["friction_factor"]*3    #
            else:                                                #
               friction_factor = factors["friction_factor"]      #
            ######################################################
      


            positions_pos  = list(v * k for v in unpacked[4:13])
            positions_neg  = list(v * k for v in unpacked[13:22])
            pos_values     = list(v * m for v in unpacked[22:31])
            neg_values     = list(v * m for v in unpacked[31:40])
            scale_val      = unpacked[40]
            friction_val   = unpacked[41] * friction_factor
            targettor      = unpacked[42]
            spring_value   = unpacked[43]
            damp_value     = [unpacked[44], unpacked[45]]
            axrange_val    = [int(unpacked[46]), int(unpacked[47])] 
            forceoff       = unpacked[48]



            ###############################
            scale         = scale_val     #
            friction      = friction_val  #
            targettor_vl  = targettor     #
            ###############################


            limit = TORQUE_LIMITS.get(axis_name, 6.7)
            if any(v > limit for v in pos_values + neg_values) and scale_val > 100:
                scale_val = 100
                print(f"⚠️ {axis_name} torque >{limit}Nm, Scaling limited to 100")

            # 更新 force profile / scaling / friction
            force_manager.set_force_profile(axis_name, pos_values, neg_values, positions_pos, positions_neg)
            force_manager.set_force_scale(axis_name, scale)
            friction_ctrl.set_friction(axis_name, friction)
            axlim_ctrl.set_axis_range(axis_name,axrange_val)
            spring_ctrl.set_pmoveback(axis_name, spring_value)
            damp_ctrl.set_damp(axis_name, damp_value)
            tartorque_ctrl.set_target_torque(axis_name, targettor_vl)
            forceoffset_ctrl.set_force_offset(axis_name, forceoff)


            
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)

            #print(f"✅ {axis_name} updated via UDP from {addr}")

            # ===================== 接收置零信号 =====================
            zero_flag = unpacked[2]                       
            hmi_test_enable = unpacked[3]
            #print(f"[INFO] zero_flag at index 42: {hmi_shake_enable}")
            #print(f"[INFO] zero_flag at index 41: {zero_flag}")
            #print(f"[INFO] zero_flag at index 43: {hmi_position_enable}")

            # ===================== HMI TEST 控制 =====================
            # HMI Test 模式 # # 0 = OFF # 1 = 抖杆 # 2 = 脉冲 # 3 = 倍脉冲 # 4 = 扫频 # 5 = 正弦 # 6 = 阶跃
            match hmi_test_enable:            
                case 0:
                    # ================= OFF =================
                    stickshaker.disable()           
                    # 停止信号发生器
                    pitch_signal_generator.reset()            
                    # 关闭俯仰位置控制
                    pos_contr.enable_pos_contr_class(AxisBitmask.Elevator, False)           
                    # 目标位置恢复 0
                    pos_contr.set_target_p_position(0.0)            
                case 1:
                    # ================= 抖杆 =================           
                    # 关闭位置测试
                    pitch_signal_generator.reset()            
                    pos_contr.enable_pos_contr_class(AxisBitmask.Elevator,False)            
                    # 启用抖杆震动控制
                    shake_force_in = 200.0
                    shake_freq_in = 10.0            
                    F = max(min(shake_force_in, 100.0), 1.0)
                    Q = max(min(shake_freq_in, 10.0), 1.0)            
                    stickshaker.set_force(F, Q)
                    stickshaker.enable()            
                case 2:
                    # ================= 脉冲 =================            
                    # 只在进入该模式时启动一次
                    if last_hmi_test_enable != 2:            
                        stickshaker.disable()            
                        pitch_signal_generator.start(2)           
                        # 开启俯仰位置控制
                        pos_contr.enable_pos_contr_class(AxisBitmask.Elevator,True)           
                    # 每个控制周期都更新
                    pitch_test_position = pitch_signal_generator.update()           
                    # 将测试信号作为俯仰目标位置
                    pos_contr.set_target_p_position(pitch_test_position)
            
                case 3:
                    # ================= 倍脉冲 =================           
                    if last_hmi_test_enable != 3:            
                        stickshaker.disable()           
                        pitch_signal_generator.start(3)            
                        pos_contr.enable_pos_contr_class(AxisBitmask.Elevator,True)            
                    # 每个周期更新
                    pitch_test_position = pitch_signal_generator.update()            
                    pos_contr.set_target_p_position(pitch_test_position)
            
                case 4:
                    # ================= 扫频 =================
                    if last_hmi_test_enable != 4:            
                        stickshaker.disable()            
                        pitch_signal_generator.start(4)           
                        pos_contr.enable_pos_contr_class( AxisBitmask.Elevator, True)            
                    # 每个周期更新
                    pitch_test_position = pitch_signal_generator.update()            
                    pos_contr.set_target_p_position(pitch_test_position)            
                case 5:
                    # ================= 正弦 =================           
                    if last_hmi_test_enable != 5:           
                        stickshaker.disable()            
                        pitch_signal_generator.start(5)           
                        pos_contr.enable_pos_contr_class(AxisBitmask.Elevator,True)
                    # 每个周期更新
                    pitch_test_position = pitch_signal_generator.update()           
                    pos_contr.set_target_p_position(pitch_test_position)          
                case 6:
                    # ================= 阶跃 =================           
                    if last_hmi_test_enable != 6:            
                        stickshaker.disable()            
                        pitch_signal_generator.start(6)            
                        pos_contr.enable_pos_contr_class(AxisBitmask.Elevator,True)
                    # 每个周期更新
                    pitch_test_position = pitch_signal_generator.update()
                    pos_contr.set_target_p_position(pitch_test_position)  
            # 保存当前模式
            last_hmi_test_enable = hmi_test_enable

            if zero_flag:
                # 获取主循环里的原始值
                ele     = pos_raw.get('pitch_raw', 0.0) / 108.6956
                ail     = pos_raw.get('roll_raw', 0.0)  / 108.6956
                rud     = pos_raw.get('yaw_raw', 0.0)   / 228
                force_p = force.get('fpitch', 0.0) * 40.0
                force_r = force.get('froll', 0.0)  * 40.0
                force_y = force.get('fyaw', 0.0)
                GlobalState.offsets = (ele, force_p, ail, force_r, rud, force_y)
            #print(f"⚠️ ZERO_FLAG=1, offsets set to {GlobalState.offsets}")           
        except Exception as e:
               print(f"[UDP ForceProfile ERROR] {e}")
               continue
threading.Thread(target=udp_force_profile_listener_bin, daemon=True).start()



# ===================== 主循环 =====================
try:
    first_iteration = True  # 初始化标定状态

    while True:
        if send_enable:
            buttons     = button_reader.read()
            positions   = position_reader.read()
            pos_raw     = pos_reader_raw.read()
            brakes      = brake_reader.read()
            force       = force_reader.read()
                        
            elevator    = positions.get('pitch', 0.0)
            aileron     = -positions.get('roll', 0.0)
            rudder      = positions.get('yaw', 0.0)

            # 原始值（编辑器）
            ele_r       = pos_raw.get('pitch_raw', 0.0) / 108.6956
            ail_r       = pos_raw.get('roll_raw', 0.0)  / 108.6956
            rud_r       = pos_raw.get('yaw_raw', 0.0)   / 228
            force_p_r   = force.get('fpitch', 0.0) * 40.0
            force_r_r   = force.get('froll', 0.0)  * 40.0
            force_y_r   = force.get('fyaw', 0.0)

            # 应用 offset
            if GlobalState.offsets is not None:
                ele     = ele_r     - GlobalState.offsets[0]
                force_p = force_p_r - GlobalState.offsets[1]
                ail     = ail_r     - GlobalState.offsets[2]
                force_r = force_r_r - GlobalState.offsets[3]
                rud     = rud_r     - GlobalState.offsets[4]
                force_y = force_y_r - GlobalState.offsets[5]
            else:
                ele, ail, rud = ele_r, ail_r, rud_r
                force_p, force_r, force_y = force_p_r, force_r_r, force_y_r
            
            brake_left  = brakes.get('brake_left', 0.0)
            brake_right = brakes.get('brake_right', 0.0)

            buttons_value = 0
            for b in buttons:
                buttons_value |= b

            #=====数据打包=====
            packet_out = struct.pack("<iffffffff", buttons_value, elevator, aileron, rudder, brake_left, brake_right,force_p/GlobalState.w,force_r,force_y)
            #print("packet_out:", packet_out.hex())
            #print("length:", len(packet_out))
            packet_out_edit_joystick = struct.pack("ffff", ele, force_p/GlobalState.w, ail, force_r)
                           

            #packet_out_edit_joystick = struct.pack("ffffff", ele, force_p*2, ail, force_r, rud, force_y)
           
           #=====数据发送=====
            sock.sendto(packet_out, (HOST_IP, HOST_PORT))
            sock.sendto(packet_out_edit_joystick, (edit_joystick_IP, edit_joystick_PORT))
        time.sleep(T)

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    print("[INFO] Exiting program...")
    sock.close()
    force_manager.close()
    if cls2sim_proc and cls2sim_proc.poll() is None:
        cls2sim_proc.terminate()
        try:
            cls2sim_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls2sim_proc.kill()
        print("[WARN] CLS2Sim killed")

