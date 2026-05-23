# 鼠标自动点击器

基于 Python + tkinter 的 Windows 桌面鼠标自动点击和键盘连按工具，支持全局热键，中文界面。

## 项目结构

```
ShubiaoDianji/
├── main.py            # 入口，创建窗口和所有模块实例
├── clicker.py         # 鼠标点击引擎：独立线程、Win32 SendInput / pynput 双模式
├── keyboarder.py      # 键盘连按引擎：多按键独立线程并发
├── hotkey.py          # 全局热键管理（pynput GlobalHotKeys）
├── ui.py              # tkinter 双标签页中文界面（鼠标 / 键盘）
├── requirements.txt   # pynput
└── dist/              # PyInstaller 打包输出
    └── 鼠标自动点击器.exe
```

## 运行方式

```bash
pip install -r requirements.txt
python main.py
```

## 打包

```bash
pyinstaller --onefile --noconsole --name "鼠标自动点击器" main.py
```

## 快捷键

| 按键 | 功能 |
|------|------|
| F6 | 鼠标点击 启停 |
| F7 | 获取当前鼠标坐标 |
| F8 | 键盘连按 启停 |

## 关键设计

- **clicker.py** — `Clicker` 类，`threading.Event` 控制启停。双发送模式：标准 pynput 和兼容 Win32（ctypes 调 `SendInput`），用于 DirectInput 游戏。支持按下时长和随机延迟。
- **keyboarder.py** — `KeyTask` 单按键连按任务，`Keyboarder` 管理器。每个按键独立线程，支持 66 种按键选择，各自配置按下时长/间隔/随机延迟。
- **hotkey.py** — `HotkeyManager` 包装 `pynput.keyboard.GlobalHotKeys`，可注册/取消多个热键。
- **ui.py** — `App(ttk.Frame)`，`ttk.Notebook` 双标签页。键盘页用 `grid` 布局对齐列。所有热键回调通过 `root.after_idle()` 调度到主线程。
