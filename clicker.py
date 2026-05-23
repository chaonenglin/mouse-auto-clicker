import threading
import time
from pynput.mouse import Button, Controller


class Clicker:
    """鼠标自动点击器核心引擎"""

    def __init__(self):
        self._interval = 1.0  # 点击间隔（秒）
        self._button = Button.left
        self._mode = "follow"  # "follow" | "fixed"
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
    def click_type(self):
        if self._button == Button.left:
            return "left"
        elif self._button == Button.right:
            return "right"
        return "middle"

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

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ("follow", "fixed"):
            raise ValueError(f"不支持的点击模式: {value}")
        self._mode = value

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
    def _click_loop(self):
        mouse = Controller()
        while self._running.is_set():
            if self._mode == "fixed":
                mouse.position = (self._fixed_x, self._fixed_y)
            mouse.click(self._button, 1)
            self._click_count += 1
            if self._on_count_changed:
                self._on_count_changed(self._click_count)
            time.sleep(self._interval)
