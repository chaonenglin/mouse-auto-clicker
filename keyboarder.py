import random
import threading
import time

from pynput.keyboard import Controller as KBController, Key

# 常用可选按键
AVAILABLE_KEYS = [
    # 字母
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
    "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    # 数字
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    # 功能键
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    # 特殊键
    "Enter", "Space", "Tab", "Esc", "Backspace", "Delete",
    "Insert", "Home", "End", "PageUp", "PageDown",
    # 方向键
    "Up", "Down", "Left", "Right",
    # 修饰键
    "Ctrl", "Alt", "Shift",
]

SPECIAL_KEY_MAP = {
    "Enter":    Key.enter,
    "Space":    Key.space,
    "Tab":      Key.tab,
    "Esc":      Key.esc,
    "Backspace": Key.backspace,
    "Delete":   Key.delete,
    "Insert":   Key.insert,
    "Home":     Key.home,
    "End":      Key.end,
    "PageUp":   Key.page_up,
    "PageDown": Key.page_down,
    "Up":       Key.up,
    "Down":     Key.down,
    "Left":     Key.left,
    "Right":    Key.right,
    "Ctrl":     Key.ctrl,
    "Alt":      Key.alt,
    "Shift":    Key.shift,
}
for i in range(1, 13):
    SPECIAL_KEY_MAP[f"F{i}"] = getattr(Key, f"f{i}")


def resolve_key(name: str):
    """把显示名称转为 pynput Key 对象"""
    if name in SPECIAL_KEY_MAP:
        return SPECIAL_KEY_MAP[name]
    if len(name) == 1:
        return name.lower()
    raise ValueError(f"不支持的按键: {name}")


class KeyTask:
    """单个按键的连按任务"""

    def __init__(self, key_name="A", press_ms=50, interval_ms=1000, jitter_ms=0):
        self.key_name = key_name
        self.press_ms = press_ms
        self.interval_ms = interval_ms
        self.jitter_ms = jitter_ms
        self._running = False
        self._thread = None
        self._count = 0

    @property
    def count(self):
        return self._count

    @property
    def is_running(self):
        return self._running

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def reset_count(self):
        self._count = 0

    def _loop(self):
        kb = KBController()
        key = resolve_key(self.key_name)
        press_sec = self.press_ms / 1000.0
        interval_sec = self.interval_ms / 1000.0
        jitter_sec = self.jitter_ms / 1000.0

        while self._running:
            kb.press(key)
            time.sleep(max(0.01, press_sec))
            kb.release(key)
            self._count += 1
            delay = interval_sec + random.uniform(-jitter_sec, jitter_sec)
            time.sleep(max(0.01, delay))


class Keyboarder:
    """键盘连按管理器"""

    def __init__(self):
        self.tasks: list[KeyTask] = []

    def add(self, task: KeyTask):
        self.tasks.append(task)

    def remove(self, index: int):
        if 0 <= index < len(self.tasks):
            self.tasks[index].stop()
            self.tasks.pop(index)

    def clear(self):
        for t in self.tasks:
            t.stop()
        self.tasks.clear()

    def start_all(self):
        for t in self.tasks:
            t.start()

    def stop_all(self):
        for t in self.tasks:
            t.stop()

    @property
    def is_running(self):
        return any(t.is_running for t in self.tasks)

    @property
    def total_count(self):
        return sum(t.count for t in self.tasks)
