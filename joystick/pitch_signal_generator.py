
import time
import math


# ============================================================
# Pitch信号参数
# ============================================================

TEST_DURATION = 6.0       # 每次测试持续时间，单位：s
AMPLITUDE = 0.5           # 幅值

# 正弦频率
SINE_FREQUENCY = 1.0      # Hz

# 扫频频率
SWEEP_START_FREQUENCY = 0.5   # Hz
SWEEP_END_FREQUENCY = 5.0     # Hz


# ============================================================
# Pitch信号发生器
# ============================================================

class PitchSignalGenerator:

    def __init__(self):

        # 当前模式# 0 = 无信号# 1 = 脉冲# 2 = 倍脉冲# 3 = 扫频# 4 = 正弦# 5 = 阶跃
        self.mode = 0
        # 信号开始时间
        self.start_time = 0.0
        # 上一次更新时间
        self.last_time = 0.0
        # 正弦信号相位
        self.phase = 0.0
        # 是否正在运行
        self.running = False
    # ========================================================
    # 开始测试
    # ========================================================
    def start(self, mode):

        if mode < 2 or mode > 6:
            return
        self.mode = mode
        self.start_time = time.perf_counter()
        self.last_time = self.start_time
        self.phase = 0.0
        self.running = True

    # ========================================================
    # 停止测试
    # ========================================================

    def reset(self):
        self.mode = 0
        self.start_time = 0.0
        self.last_time = 0.0
        self.phase = 0.0
        self.running = False

    # ========================================================
    # 更新信号
    #
    # 返回值：
    # -1.0 ~ +1.0
    # ========================================================

    def update(self):
        # 当前没有测试
        if not self.running:
            return 0.0
        # 当前时间
        now = time.perf_counter()
        # 测试已经运行的时间
        t = now - self.start_time
        # 当前周期
        dt = now - self.last_time
        self.last_time = now

        # ====================================================
        # 6秒测试结束
        # ====================================================

        if t >= TEST_DURATION:

            self.reset()

            return 0.0

        # ====================================================
        # Mode 2：脉冲
        #
        # 0~1s    +0.5
        # 1~2s     0
        # 2~3s    +0.5
        # 3~4s     0
        # 4~5s    +0.5
        # 5~6s     0
        # ====================================================

        if self.mode == 2:
            pulse_period = 2.0
            cycle_time = t % pulse_period
            if cycle_time < 1.0:
                output = AMPLITUDE
            else:
                output = 0.0

        # ====================================================
        # Mode 3：倍脉冲
        #
        # 0~1s    +0.5
        # 1~2s     0
        # 2~3s    -0.5
        # 3~6s     0
        # ====================================================

        elif self.mode == 3:
            if t < 1.0:
                output = AMPLITUDE
            elif t < 2.0:
                output = 0.0
            elif t < 3.0:
                output = -AMPLITUDE
            else:
                output = 0.0

        # ====================================================
        # Mode 4：扫频
        #
        # 0.5Hz → 5Hz
        # 持续6秒
        # ====================================================

        elif self.mode == 4:

            # 当前频率
            frequency = (SWEEP_START_FREQUENCY + (SWEEP_END_FREQUENCY - SWEEP_START_FREQUENCY ) * (t / TEST_DURATION) )
            # 相位积分
            self.phase += (2.0* math.pi * frequency* dt )
            output = (
                AMPLITUDE* math.sin(self.phase))

        # ====================================================
        # Mode 5：正弦
        #
        # 频率：1Hz
        # 幅值：0.5
        # ====================================================

        elif self.mode == 5:
            frequency = SINE_FREQUENCY
            # 相位积分
            self.phase += (
                2.0* math.pi* frequency* dt)
            output = ( AMPLITUDE* math.sin(self.phase))
        # ====================================================
        # Mode 6：阶跃
        #
        # 0~6s：+0.5
        # 6s：恢复0
        # ====================================================

        elif self.mode == 6:
            output = AMPLITUDE
        else:
            output = 0.0
        # ====================================================
        # 限幅
        # ====================================================
        output = max(-1.0, min(1.0, output))
        return output
