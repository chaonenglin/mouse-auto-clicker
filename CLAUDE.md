# 鼠标自动点击器

基于 Python + tkinter 的 Windows 桌面鼠标自动点击工具，支持全局热键，中文界面。

## 项目结构

```
ShubiaoDianji/
├── main.py            # 入口，启动 GUI
├── clicker.py         # 点击引擎：独立线程循环点击
├── hotkey.py          # 全局热键管理（pynput GlobalHotKeys）
├── ui.py              # tkinter 中文界面
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

## 关键设计

- **clicker.py** — `Clicker` 类，通过 `threading.Event` 控制点击循环启停，内部用 `pynput.mouse.Controller` 执行点击。回调 `_on_count_changed` 更新 UI 计数。
- **hotkey.py** — `HotkeyManager` 包装 `pynput.keyboard.GlobalHotKeys`，支持注册/取消热键。F6 启停点击，F7 取当前坐标。
- **ui.py** — `App(ttk.Frame)`，所有热键回调通过 `root.after_idle()` 调度到主线程确保线程安全。
