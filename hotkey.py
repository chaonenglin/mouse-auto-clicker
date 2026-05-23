from pynput.keyboard import Key, GlobalHotKeys


class HotkeyManager:
    """全局热键管理器"""

    def __init__(self):
        self._listener = None
        self._callbacks = {}

    def register(self, hotkey_str, callback):
        """注册热键，hotkey_str 如 '<ctrl>+<f6>'"""
        self._callbacks[hotkey_str] = callback
        self._restart()

    def unregister(self, hotkey_str):
        self._callbacks.pop(hotkey_str, None)
        self._restart()

    def _on_activate(self, hotkey_str):
        def handler():
            cb = self._callbacks.get(hotkey_str)
            if cb:
                cb()
        return handler

    def _restart(self):
        if self._listener:
            self._listener.stop()
        if not self._callbacks:
            return
        mapping = {k: self._on_activate(k) for k in self._callbacks}
        self._listener = GlobalHotKeys(mapping)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
