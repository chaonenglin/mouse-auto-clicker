import tkinter as tk

from clicker import Clicker
from hotkey import HotkeyManager
from keyboarder import Keyboarder
from ui import App


def main():
    root = tk.Tk()
    root.title("鼠标自动点击器")
    root.resizable(False, False)

    root.update_idletasks()
    w, h = 640, 560
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    clicker = Clicker()
    keyboarder = Keyboarder()
    hotkey_mgr = HotkeyManager()

    app = App(root, clicker, hotkey_mgr, keyboarder)

    root.protocol("WM_DELETE_WINDOW", lambda: (app.shutdown(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
