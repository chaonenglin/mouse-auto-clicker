import tkinter as tk
from tkinter import ttk


class App(ttk.Frame):
    """中文 UI 主界面"""

    def __init__(self, root, clicker, hotkey_mgr):
        super().__init__(root, padding=16)
        self.root = root
        self.clicker = clicker
        self.hotkey_mgr = hotkey_mgr
        self._count_var = tk.StringVar(value="0")
        self._status_var = tk.StringVar(value="已停止")
        self._hotkey_var = tk.StringVar(value="F6")

        self.clicker.set_count_callback(self._on_count)

        self._build()
        self._bind_hotkey()

    # ================================================================
    # 界面构建
    # ================================================================

    def _build(self):
        self._title_label()
        self._settings_frame()
        self._control_frame()
        self._bottom_bar()
        self.pack(fill="both", expand=True)

    def _title_label(self):
        label = ttk.Label(self, text="鼠标自动点击器", font=("Microsoft YaHei", 16, "bold"))
        label.pack(pady=(0, 12))

    def _settings_frame(self):
        frame = ttk.LabelFrame(self, text="设置", padding=10)
        frame.pack(fill="x", pady=(0, 10))

        # 第一行：点击间隔 | 点击类型
        row1 = ttk.Frame(frame)
        row1.pack(fill="x", pady=(0, 6))
        ttk.Label(row1, text="点击间隔：", width=10, anchor="e").pack(side="left")
        self._interval_sb = ttk.Spinbox(row1, from_=10, to=60000, width=8)
        self._interval_sb.set(1000)
        self._interval_sb.pack(side="left", padx=(0, 16))
        ttk.Label(row1, text="毫秒", font=("Microsoft YaHei", 9)).pack(side="left", padx=(0, 20))

        ttk.Label(row1, text="点击类型：", width=10, anchor="e").pack(side="left")
        self._type_cb = ttk.Combobox(row1, values=["左键", "右键", "中键"], state="readonly", width=6)
        self._type_cb.current(0)
        self._type_cb.pack(side="left")

        # 第二行：点击模式
        row2 = ttk.Frame(frame)
        row2.pack(fill="x", pady=(0, 6))
        ttk.Label(row2, text="点击模式：", width=10, anchor="e").pack(side="left")
        self._mode_cb = ttk.Combobox(row2, values=["跟随鼠标", "固定坐标"], state="readonly", width=8)
        self._mode_cb.current(0)
        self._mode_cb.pack(side="left")
        self._mode_cb.bind("<<ComboboxSelected>>", self._on_mode_change)

        # 第三行：固定坐标
        row3 = ttk.Frame(frame)
        row3.pack(fill="x", pady=(0, 6))
        ttk.Label(row3, text="固定坐标：", width=10, anchor="e").pack(side="left")
        self._pos_frame = ttk.Frame(row3)
        self._pos_frame.pack(side="left")
        ttk.Label(self._pos_frame, text="X:").pack(side="left")
        self._x_entry = ttk.Entry(self._pos_frame, width=6)
        self._x_entry.insert(0, "0")
        self._x_entry.pack(side="left", padx=(2, 8))
        ttk.Label(self._pos_frame, text="Y:").pack(side="left")
        self._y_entry = ttk.Entry(self._pos_frame, width=6)
        self._y_entry.insert(0, "0")
        self._y_entry.pack(side="left", padx=(2, 0))

        ttk.Button(row3, text="取当前", command=self._pick_position, width=7).pack(side="left", padx=(8, 0))
        ttk.Label(row3, text="  （快捷键 F7）", foreground="gray", font=("Microsoft YaHei", 8)).pack(side="left")

        self._set_fixed_state("disabled")

        # 第四行：热键
        row4 = ttk.Frame(frame)
        row4.pack(fill="x")
        ttk.Label(row4, text="启停热键：", width=10, anchor="e").pack(side="left")
        self._hotkey_entry = ttk.Entry(row4, width=10, textvariable=self._hotkey_var)
        self._hotkey_entry.pack(side="left")
        self._hotkey_entry.bind("<FocusOut>", self._on_hotkey_change)
        self._hotkey_entry.bind("<Return>", self._on_hotkey_change)
        ttk.Label(row4, text="  （修改后回车生效）", foreground="gray", font=("Microsoft YaHei", 8)).pack(side="left")

    def _control_frame(self):
        frame = ttk.LabelFrame(self, text="控制", padding=10)
        frame.pack(fill="x", pady=(0, 10))

        # 开始 / 停止按钮
        self._start_btn = ttk.Button(frame, text="开 始", command=self._toggle)
        self._start_btn.pack(pady=(0, 8))

        # 状态行
        status_row = ttk.Frame(frame)
        status_row.pack(fill="x", pady=(0, 4))
        ttk.Label(status_row, text="状态：", width=10, anchor="e").pack(side="left")
        self._status_label = ttk.Label(status_row, textvariable=self._status_var, foreground="gray")
        self._status_label.pack(side="left")

        # 次数行
        count_row = ttk.Frame(frame)
        count_row.pack(fill="x")
        ttk.Label(count_row, text="点击次数：", width=10, anchor="e").pack(side="left")
        ttk.Label(count_row, textvariable=self._count_var).pack(side="left")

    def _bottom_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x")
        self._top_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="窗口置顶", variable=self._top_var, command=self._toggle_top).pack(side="left")
        ttk.Button(bar, text="重置计数", command=self._reset_count).pack(side="right")

    # ================================================================
    # 业务逻辑 — 设置同步
    # ================================================================

    def _read_settings(self):
        """从界面读取所有设置并同步到 Clicker"""
        self.clicker.interval_ms = float(self._interval_sb.get())

        type_map = {"左键": "left", "右键": "right", "中键": "middle"}
        self.clicker.click_type = type_map[self._type_cb.get()]

        if self._mode_cb.get() == "固定坐标":
            self.clicker.mode = "fixed"
            try:
                x = int(self._x_entry.get())
                y = int(self._y_entry.get())
                self.clicker.set_fixed_position(x, y)
            except ValueError:
                pass
        else:
            self.clicker.mode = "follow"

    # ================================================================
    # 事件处理
    # ================================================================

    def _toggle(self):
        self._read_settings()
        self.clicker.toggle()
        self._update_ui()

    def _update_ui(self):
        if self.clicker.is_running:
            self._start_btn.configure(text="停 止")
            self._status_var.set("运行中")
            self._status_label.configure(foreground="green")
        else:
            self._start_btn.configure(text="开 始")
            self._status_var.set("已停止")
            self._status_label.configure(foreground="gray")

    def _on_count(self, count):
        self.root.after_idle(lambda: self._count_var.set(str(count)))

    def _on_mode_change(self, event=None):
        if self._mode_cb.get() == "固定坐标":
            self._set_fixed_state("normal")
        else:
            self._set_fixed_state("disabled")

    def _set_fixed_state(self, state):
        for child in self._pos_frame.winfo_children():
            try:
                child.configure(state=state)
            except Exception:
                pass

    def _pick_position(self):
        """获取当前鼠标位置"""
        from pynput.mouse import Controller

        mouse = Controller()
        pos = mouse.position
        self._x_entry.delete(0, "end")
        self._x_entry.insert(0, str(int(pos[0])))
        self._y_entry.delete(0, "end")
        self._y_entry.insert(0, str(int(pos[1])))

    def _pick_position_hotkey(self):
        """F7 热键触发：调度到主线程执行"""
        self.root.after_idle(self._pick_position)

    def _toggle_top(self):
        self.root.attributes("-topmost", self._top_var.get())

    def _reset_count(self):
        self.clicker.reset_count()
        self._count_var.set("0")

    # ================================================================
    # 热键
    # ================================================================

    def _bind_hotkey(self):
        hotkey = self._hotkey_var.get().strip()
        self._normalize_and_bind(hotkey)
        # 固定注册 F7 用于获取鼠标位置
        self.hotkey_mgr.register("<f7>", self._pick_position_hotkey)

    def _on_hotkey_change(self, event=None):
        new_hotkey = self._hotkey_var.get().strip()
        if new_hotkey:
            self._normalize_and_bind(new_hotkey)

    def _normalize_and_bind(self, text):
        """把用户输入(如 F6 / ctrl+f6) 转为 pynput GlobalHotKeys 格式"""
        self.hotkey_mgr.unregister("<f6>")  # 清除旧默认
        key = text.replace(" ", "")
        # 转换为 pynput 格式
        parts = key.lower().split("+")
        converted = []
        for p in parts:
            p = p.strip()
            if p.startswith("f") and p[1:].isdigit():
                converted.append(f"<{p}>")
            elif p in ("ctrl", "shift", "alt", "cmd"):
                converted.append(f"<{p}>")
            else:
                converted.append(p)
        hotkey_str = "+".join(converted)
        self.hotkey_mgr.register(hotkey_str, self._hotkey_action)

    def _hotkey_action(self):
        """热键触发：同步设置 → 切换（来自 pynput 线程，需要调度到主线程）"""
        self.root.after_idle(self._toggle)

    # ================================================================
    # 生命周期
    # ================================================================

    def shutdown(self):
        self.clicker.stop()
        self.hotkey_mgr.stop()
