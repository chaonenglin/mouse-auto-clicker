import ctypes
import random
import threading
import time
from ctypes import wintypes

from pynput.mouse import Button, Controller

# ================================================================
# Windows SendInput 底层 API（兼容 DirectInput 游戏）
# ================================================================

SendInput = ctypes.windll.user32.SendInput
SetCursorPos = ctypes.windll.user32.SetCursorPos

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

DOWN_MAP = {
    "left": MOUSEEVENTF_LEFTDOWN,
    "right": MOUSEEVENTF_RIGHTDOWN,
    "middle": MOUSEEVENTF_MIDDLEDOWN,
}
UP_MAP = {
    "left": MOUSEEVENTF_LEFTUP,
    "right": MOUSEEVENTF_RIGHTUP,
    "middle": MOUSEEVENTF_MIDDLEUP,
}


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("mi", MOUSEINPUT),
    ]


def _inject_mouse(dw_flags, dx=0, dy=0):
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.mi.dx = dx
    inp.mi.dy = dy
    inp.mi.mouseData = 0
    inp.mi.dwFlags = dw_flags
    inp.mi.time = 0
    inp.mi.dwExtraInfo = None
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def win32_click(button: str):
    """使用 SendInput 直接注入鼠标事件"""
    _inject_mouse(DOWN_MAP[button])
    _inject_mouse(UP_MAP[button])


def win32_press(button: str):
    _inject_mouse(DOWN_MAP[button])


def win32_release(button: str):
    _inject_mouse(UP_MAP[button])


def win32_move(x: int, y: int):
    """移动鼠标到绝对坐标"""
    SetCursorPos(x, y)


# ================================================================
# Clicker 引擎
# ================================================================


class Clicker:
    """鼠标自动点击器核心引擎"""

    def __init__(self):
        self._interval = 1.0
        self._jitter = 0.0  # 随机延迟范围（秒）
        self._press_duration = 0.05
        self._button = Button.left
        self._button_str = "left"
        self._mode = "follow"
        self._send_mode = "pynput"  # "pynput" | "win32"
        self._fixed_x = 0
        self._fixed_y = 0
        self._running = threading.Event()
        self._thread = None
        self._click_count = 0
        self._on_count_changed = None

    # --- 属性 ---
    @property
    def is_running(self):
        return self._running.is_set()

    @property
    def click_count(self):
        return self._click_count

    @property
    def interval_ms(self):
        return int(self._interval * 1000)

    @interval_ms.setter
    def interval_ms(self, value):
        self._interval = max(0.01, value / 1000.0)

    @property
    def press_ms(self):
        return int(self._press_duration * 1000)

    @press_ms.setter
    def press_ms(self, value):
        self._press_duration = max(0.01, value / 1000.0)

    @property
    def jitter_ms(self):
        return int(self._jitter * 1000)

    @jitter_ms.setter
    def jitter_ms(self, value):
        self._jitter = max(0, value / 1000.0)

    @property
    def click_type(self):
        return self._button_str

    @click_type.setter
    def click_type(self, value):
        if value == "left":
            self._button = Button.left
        elif value == "right":
            self._button = Button.right
        elif value == "middle":
            self._button = Button.middle
        else:
            raise ValueError(f"不支持的点击类型: {value}")
        self._button_str = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ("follow", "fixed"):
            raise ValueError(f"不支持的点击模式: {value}")
        self._mode = value

    @property
    def send_mode(self):
        return self._send_mode

    @send_mode.setter
    def send_mode(self, value):
        if value not in ("pynput", "win32"):
            raise ValueError(f"不支持的发送模式: {value}")
        self._send_mode = value

    def set_fixed_position(self, x, y):
        self._fixed_x = x
        self._fixed_y = y

    def set_count_callback(self, callback):
        self._on_count_changed = callback

    # --- 控制 ---
    def start(self):
        if self.is_running:
            return
        self._running.set()
        self._thread = threading.Thread(target=self._click_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running.clear()

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def reset_count(self):
        self._click_count = 0

    # --- 内部 ---
    def _move_to(self, x, y):
        if self._send_mode == "win32":
            win32_move(x, y)
        else:
            self._pynput_mouse.position = (x, y)

    def _press(self):
        if self._send_mode == "win32":
            win32_press(self._button_str)
        else:
            self._pynput_mouse.press(self._button)

    def _release(self):
        if self._send_mode == "win32":
            win32_release(self._button_str)
        else:
            self._pynput_mouse.release(self._button)

    def _click_loop(self):
        self._pynput_mouse = Controller()
        while self._running.is_set():
            if self._mode == "fixed":
                self._move_to(self._fixed_x, self._fixed_y)
            self._press()
            time.sleep(self._press_duration)
            self._release()
            self._click_count += 1
            if self._on_count_changed:
                self._on_count_changed(self._click_count)
            delay = self._interval + random.uniform(-self._jitter, self._jitter)
            time.sleep(max(0.01, delay))
