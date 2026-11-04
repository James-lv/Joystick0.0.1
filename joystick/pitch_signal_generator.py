#import time
#import math
#
#
## ============================================================
## Pitch信号参数
## ============================================================
#
#TEST_DURATION = 6.0       # 每次测试持续时间，单位：s
#AMPLITUDE = 0.5           # 幅值
#
## 正弦频率
#SINE_FREQUENCY = 0.5      # Hz
#
## 扫频频率
#SWEEP_START_FREQUENCY = 0.1   # Hz
#SWEEP_END_FREQUENCY = 1     # Hz
#
#
## ============================================================
## Pitch信号发生器
## ============================================================
#
#class PitchSignalGenerator:
#
#    def __init__(self):
#
#        # 当前模式# 0 = 无信号# 1 = 脉冲# 2 = 倍脉冲# 3 = 扫频# 4 = 正弦# 5 = 阶跃
#        self.mode = 0
#        # 信号开始时间
#        self.start_time = 0.0
#        # 上一次更新时间
#        self.last_time = 0.0
#        # 正弦信号相位
#        self.phase = 0.0
#        # 是否正在运行
#        self.running = False
#    # ========================================================
#    # 开始测试
#    # ========================================================
#    def start(self, mode):
#
#        if mode < 2 or mode > 6:
#            return
#        self.mode = mode
#        self.start_time = time.perf_counter()
#        self.last_time = self.start_time
#        self.phase = 0.0
#        self.running = True
#
#        print(f"[START] mode={mode}, start_time={self.start_time:.6f}")
#
#    # ========================================================
#    # 停止测试
#    # ========================================================
#
#    def reset(self):
#        self.mode = 0
#        self.start_time = 0.0
#        self.last_time = 0.0
#        self.phase = 0.0
#        self.running = False
#
#    # ========================================================
#    # 更新信号
#    #
#    # 返回值：
#    # -1.0 ~ +1.0
#    # ========================================================
#
#    def update(self):
#        now = time.perf_counter()
#        t = now - self.start_time
#        
#        print(
#            f"now={now:.6f}, "
#            f"start={self.start_time:.6f}, "
#            f"t={t:.3f}"
#        )
#        # 当前没有测试
#        if not self.running:
#            return 0.0
#        # 当前时间
#        now = time.perf_counter()
#        # 测试已经运行的时间
#        t = now - self.start_time
#        # 当前周期
#        dt = now - self.last_time
#        self.last_time = now
#
#        # ====================================================
#        # 6秒测试结束
#        # ====================================================
#
#        if t >= TEST_DURATION:
#
#            self.reset()
#
#            return 0.0
#
#        # ====================================================
#        # Mode 2：脉冲
#        #
#        # 0~1s    +0.5
#        # 1~2s     0
#        # 2~3s    +0.5
#        # 3~4s     0
#        # 4~5s    +0.5
#        # 5~6s     0
#        # ====================================================
#
#        if self.mode == 2:
#            if t < 1.0:
#              output = 0.0
#            elif t < 2.0:
#                output = 0.6
#            else:
#                output = 0.0
#            
#
#        # ====================================================
#        # Mode 3：倍脉冲
#        #
#        # 0~1s    +0.5
#        # 1~2s     0
#        # 2~3s    -0.5
#        # 3~6s     0
#        # ====================================================
#
#        elif self.mode == 3:
#             if t < 1.0:
#                 output = 0.0
#             
#             elif t < 2.0:
#                 # 0 -> +0.5
#                 output = AMPLITUDE * (t - 1.0)
#             
#             elif t < 3.0:
#                 # +0.5 -> 0
#                 output = AMPLITUDE * (3.0 - t)
#             
#             elif t < 4.0:
#                 # 0 -> -0.5
#                 output = -AMPLITUDE * (t - 3.0)
#             
#             elif t < 5.0:
#                 # -0.5 -> 0
#                 output = -AMPLITUDE * (5.0 - t)
#             
#             else:
#                 output = 0.0
#
#        # ====================================================
#        # Mode 4：扫频
#        #
#        # 0.5Hz → 5Hz
#        # 持续6秒
#        # ====================================================
#
#        elif self.mode == 4:
#
#            # 当前频率
#            frequency = (SWEEP_START_FREQUENCY + (SWEEP_END_FREQUENCY - SWEEP_START_FREQUENCY ) * (t / TEST_DURATION) )
#            # 相位积分
#            self.phase += (2.0* math.pi * frequency* dt )
#            output = (
#                AMPLITUDE* math.sin(self.phase))
#
#        # ====================================================
#        # Mode 5：正弦
#        #
#        # 频率：1Hz
#        # 幅值：0.5
#        # ====================================================
#
#        elif self.mode == 5:
#            frequency = SINE_FREQUENCY
#            # 相位积分
#            self.phase += (
#                2.0* math.pi* frequency* dt)
#            output = ( AMPLITUDE* math.sin(self.phase))
#        # ====================================================
#        # Mode 6：阶跃
#        #
#        # 0~6s：+0.5
#        # 6s：恢复0
#        # ====================================================
#
#        elif self.mode == 6:
#            output = AMPLITUDE
#        else:
#            output = 0.0
#        # ====================================================
#        # 限幅
#        # ====================================================
#        output = max(-1.0, min(1.0, output))
#        
#        print(
#              f"[DEBUG] mode={self.mode}, "
#              f"running={self.running}, "
#              f"t={t:.3f}, "
#              f"dt={dt:.6f}, "
#              f"phase={self.phase:.6f}, "
#              f"output={output:.6f}")             
#
#
#
#
#
#
#
#        return output
#


import time
import math
import threading

TEST_DURATION = 8.0
AMPLITUDE = 0.5

SINE_FREQUENCY = 0.5
SWEEP_START_FREQUENCY = 0.1
SWEEP_END_FREQUENCY = 1.0


class PitchSignalGenerator:

    def __init__(self):
        self.mode = 0
        self.start_time = 0.0
        self.phase = 0.0
        self.running = False

        self.output = 0.0
        self.lock = threading.Lock()
        self.thread = None

    def start(self, mode):

        if mode < 2 or mode > 6:
            return

        self.stop()

        with self.lock:
            self.mode = mode
            self.start_time = time.perf_counter()
            self.phase = 0.0
            self.output = 0.0
            self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self.thread.start()

    def stop(self):

        with self.lock:
            self.running = False
            self.output = 0.0
            self.mode = 0

    def get_output(self):
        with self.lock:
            return self.output

    def _run(self):

        last_time = time.perf_counter()

        while True:

            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            with self.lock:

                if not self.running:
                    break

                t = now - self.start_time
                mode = self.mode

                if t >= TEST_DURATION:
                    self.running = False
                    self.mode = 0
                    self.output = 0.0
                    break

                # Mode 2：周期脉冲
                if mode == 2:
                        output = AMPLITUDE 
                        if 0.0 <= t < 1.0 :
                            output = AMPLITUDE 
                        else :
                            output=0.0
                        print(f"[PULSE] t={t:.3f}, output={output:.3f}")
                # Mode 3：正负双脉冲
                elif mode == 3:
                     if 0.0 <= t < 1.0:
        # 0 -> +0.5
                        output = AMPLITUDE * t

                     elif 1.0 <= t < 2.0:
                         # +0.5 -> 0
                         output = AMPLITUDE * (2.0 - t)
                     
                     elif 2.0 <= t < 3.0:
                         # 0 -> -0.5
                         output = -AMPLITUDE * (t - 2.0)
                     
                     elif 3.0 <= t < 4.0:
                         # -0.5 -> 0
                         output = -AMPLITUDE * (4.0 - t)
                     
                     else:
                                output = 0.0
                            
                # Mode 4：扫频正弦
                elif mode == 4:
                    frequency = (
                        SWEEP_START_FREQUENCY
                        + (SWEEP_END_FREQUENCY - SWEEP_START_FREQUENCY)
                        * (t / TEST_DURATION)
                    )

                    self.phase += 2.0 * math.pi * frequency * dt
                    output = AMPLITUDE * math.sin(self.phase)

                # Mode 5：固定频率正弦
                elif mode == 5:
                    self.phase += 2.0 * math.pi * SINE_FREQUENCY * dt
                    output = AMPLITUDE * math.sin(self.phase)

                # Mode 6：阶跃
                elif mode == 6:
                    output = AMPLITUDE if 1.0 <= t < 5.0 else 0.0

                else:
                    output = 0.0

                self.output = max(-1.0, min(1.0, output))

            # 后台更新周期约1ms
            time.sleep(0.001)