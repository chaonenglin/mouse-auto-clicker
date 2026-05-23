import tkinter as tk
from tkinter import ttk

from keyboarder import AVAILABLE_KEYS, KeyTask


class App(ttk.Frame):
    """中文 UI 主界面 — 双标签页"""

    def __init__(self, root, clicker, hotkey_mgr, keyboarder):
        super().__init__(root, padding=12)
        self.root = root
        self.clicker = clicker
        self.hotkey_mgr = hotkey_mgr
        self.keyboarder = keyboarder

        self._count_var = tk.StringVar(value="0")
        self._status_var = tk.StringVar(value="已停止")
        self._kb_count_var = tk.StringVar(value="0")
        self._hotkey_var = tk.StringVar(value="F6")

        self.clicker.set_count_callback(self._on_mouse_count)
        self._kb_task_rows = []

        self._build()
        self._bind_hotkey()

    # ================================================================
    # 整体布局
    # ================================================================
    def _build(self):
        ttk.Label(self, text="鼠标自动点击器", font=("Microsoft YaHei", 16, "bold")).pack(pady=(0, 10))
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        notebook.add(self._mouse_tab(), text="鼠标点击")
        notebook.add(self._keyboard_tab(), text="键盘连按")
        self._bottom_bar()
        self.pack(fill="both", expand=True)

    # ================================================================
    # 鼠标点击页
    # ================================================================
    def _mouse_tab(self):
        tab = ttk.Frame(self, padding=8)

        frame = ttk.LabelFrame(tab, text="鼠标设置", padding=10)
        frame.pack(fill="x")

        # row1: 间隔 | 随机延迟 | 按下时长
        r1 = ttk.Frame(frame); r1.pack(fill="x", pady=(0,6))
        ttk.Label(r1, text="点击间隔：", width=10, anchor="e").pack(side="left")
        self._interval_sb = ttk.Spinbox(r1, from_=10, to=60000, width=6)
        self._interval_sb.set(1000); self._interval_sb.pack(side="left")
        ttk.Label(r1, text="ms", font=("Microsoft YaHei",8)).pack(side="left", padx=(2,8))

        ttk.Label(r1, text="随机延迟：", width=10, anchor="e").pack(side="left")
        self._jitter_sb = ttk.Spinbox(r1, from_=0, to=5000, width=6)
        self._jitter_sb.set(0); self._jitter_sb.pack(side="left")
        ttk.Label(r1, text="ms", font=("Microsoft YaHei",8)).pack(side="left", padx=(2,8))

        ttk.Label(r1, text="按下时长：", width=10, anchor="e").pack(side="left")
        self._press_sb = ttk.Spinbox(r1, from_=10, to=5000, width=6)
        self._press_sb.set(50); self._press_sb.pack(side="left")
        ttk.Label(r1, text="ms", font=("Microsoft YaHei",8)).pack(side="left", padx=(2,12))

        # row2: 点击类型 | 点击模式 | 发送模式
        r2 = ttk.Frame(frame); r2.pack(fill="x", pady=(0,6))
        ttk.Label(r2, text="点击类型：", width=10, anchor="e").pack(side="left")
        self._type_cb = ttk.Combobox(r2, values=["左键","右键","中键"], state="readonly", width=6)
        self._type_cb.current(0); self._type_cb.pack(side="left", padx=(0,8))

        ttk.Label(r2, text="点击模式：", width=10, anchor="e").pack(side="left")
        self._mode_cb = ttk.Combobox(r2, values=["跟随鼠标","固定坐标"], state="readonly", width=8)
        self._mode_cb.current(0); self._mode_cb.pack(side="left", padx=(0,8))
        self._mode_cb.bind("<<ComboboxSelected>>", self._on_mode_change)

        ttk.Label(r2, text="发送模式：", width=10, anchor="e").pack(side="left")
        self._send_mode_cb = ttk.Combobox(r2, values=["标准 (pynput)","兼容 (Win32)"], state="readonly", width=12)
        self._send_mode_cb.current(0); self._send_mode_cb.pack(side="left")
        ttk.Label(r2, text="  游戏无效时选兼容", foreground="gray", font=("Microsoft YaHei",8)).pack(side="left")

        # row3: 固定坐标
        r3 = ttk.Frame(frame); r3.pack(fill="x", pady=(0,6))
        ttk.Label(r3, text="固定坐标：", width=10, anchor="e").pack(side="left")
        self._pos_frame = ttk.Frame(r3); self._pos_frame.pack(side="left")
        ttk.Label(self._pos_frame, text="X:").pack(side="left")
        self._x_entry = ttk.Entry(self._pos_frame, width=6)
        self._x_entry.insert(0,"0"); self._x_entry.pack(side="left", padx=(2,8))
        ttk.Label(self._pos_frame, text="Y:").pack(side="left")
        self._y_entry = ttk.Entry(self._pos_frame, width=6)
        self._y_entry.insert(0,"0"); self._y_entry.pack(side="left", padx=(2,0))
        ttk.Button(r3, text="取当前", command=self._pick_position, width=7).pack(side="left", padx=(8,0))
        ttk.Label(r3, text="  （快捷键 F7）", foreground="gray", font=("Microsoft YaHei",8)).pack(side="left")
        self._set_fixed_state("disabled")

        # row4: 热键
        r4 = ttk.Frame(frame); r4.pack(fill="x")
        ttk.Label(r4, text="启停热键：", width=10, anchor="e").pack(side="left")
        self._hotkey_entry = ttk.Entry(r4, width=10, textvariable=self._hotkey_var)
        self._hotkey_entry.pack(side="left")
        self._hotkey_entry.bind("<FocusOut>", self._on_hotkey_change)
        self._hotkey_entry.bind("<Return>", self._on_hotkey_change)
        ttk.Label(r4, text="  （修改后回车生效）", foreground="gray", font=("Microsoft YaHei",8)).pack(side="left")

        # 控制区
        ctrl = ttk.LabelFrame(tab, text="控制", padding=10)
        ctrl.pack(fill="x", pady=(8,0))

        self._start_btn = ttk.Button(ctrl, text="开 始", command=self._toggle_mouse)
        self._start_btn.pack(pady=(0,6))
        ttk.Label(ctrl, text="快捷键 F6", foreground="gray", font=("Microsoft YaHei",8)).pack()

        sr = ttk.Frame(ctrl); sr.pack(fill="x", pady=(0,2))
        ttk.Label(sr, text="状态：", width=10, anchor="e").pack(side="left")
        self._status_label = ttk.Label(sr, textvariable=self._status_var, foreground="gray")
        self._status_label.pack(side="left")

        cr = ttk.Frame(ctrl); cr.pack(fill="x")
        ttk.Label(cr, text="点击次数：", width=10, anchor="e").pack(side="left")
        ttk.Label(cr, textvariable=self._count_var).pack(side="left")

        return tab

    # ================================================================
    # 键盘连按页
    # ================================================================
    def _keyboard_tab(self):
        tab = ttk.Frame(self, padding=8)

        list_frame = ttk.LabelFrame(tab, text="按键列表", padding=8)
        list_frame.pack(fill="both", expand=True)

        # 可滚动区域
        self._kb_canvas = tk.Canvas(list_frame, height=160, highlightthickness=0)
        self._kb_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self._kb_canvas.yview)
        self._kb_rows_frame = ttk.Frame(self._kb_canvas)

        self._kb_rows_frame.bind("<Configure>",
            lambda e: self._kb_canvas.configure(scrollregion=self._kb_canvas.bbox("all")))
        self._kb_canvas.create_window((0,0), window=self._kb_rows_frame, anchor="nw")
        self._kb_canvas.configure(yscrollcommand=self._kb_scrollbar.set)

        self._kb_canvas.pack(side="left", fill="both", expand=True)
        self._kb_scrollbar.pack(side="right", fill="y")

        # 表头（放在 rows_frame 顶部，用 grid 对齐）
        self._kb_rows_frame.columnconfigure(0, minsize=90)
        self._kb_rows_frame.columnconfigure(1, minsize=100)
        self._kb_rows_frame.columnconfigure(2, minsize=100)
        self._kb_rows_frame.columnconfigure(3, minsize=100)
        self._kb_rows_frame.columnconfigure(4, minsize=30)

        ttk.Label(self._kb_rows_frame, text="按键", font=("Microsoft YaHei",9,"bold")).grid(row=0, column=0, sticky="w", pady=(0,4))
        ttk.Label(self._kb_rows_frame, text="按下时长", font=("Microsoft YaHei",9,"bold")).grid(row=0, column=1, sticky="w", pady=(0,4), padx=(4,0))
        ttk.Label(self._kb_rows_frame, text="间隔", font=("Microsoft YaHei",9,"bold")).grid(row=0, column=2, sticky="w", pady=(0,4), padx=(4,0))
        ttk.Label(self._kb_rows_frame, text="随机", font=("Microsoft YaHei",9,"bold")).grid(row=0, column=3, sticky="w", pady=(0,4), padx=(4,0))

        # 增删按钮
        btn_row = ttk.Frame(tab); btn_row.pack(fill="x", pady=(6,0))
        ttk.Button(btn_row, text="＋ 添加按键", command=self._add_key_row).pack(side="left")
        ttk.Button(btn_row, text="清空列表", command=self._clear_key_rows).pack(side="left", padx=(8,0))

        # 控制区
        ctrl = ttk.LabelFrame(tab, text="控制", padding=10)
        ctrl.pack(fill="x", pady=(8,0))

        self._kb_start_btn = ttk.Button(ctrl, text="开 始", command=self._toggle_keyboard)
        self._kb_start_btn.pack(pady=(0,6))
        ttk.Label(ctrl, text="快捷键 F8", foreground="gray", font=("Microsoft YaHei",8)).pack()

        sr = ttk.Frame(ctrl); sr.pack(fill="x", pady=(0,2))
        ttk.Label(sr, text="状态：", width=10, anchor="e").pack(side="left")
        self._kb_status_label = ttk.Label(sr, text="已停止", foreground="gray")
        self._kb_status_label.pack(side="left")

        cr = ttk.Frame(ctrl); cr.pack(fill="x")
        ttk.Label(cr, text="按键次数：", width=10, anchor="e").pack(side="left")
        ttk.Label(cr, textvariable=self._kb_count_var).pack(side="left")

        self._next_row = 1
        self._add_key_row()
        self._kb_poll()

        return tab

    def _add_key_row(self):
        row_frame = self._kb_rows_frame
        r = self._next_row
        self._next_row += 1

        cb = ttk.Combobox(row_frame, values=AVAILABLE_KEYS, width=10)
        cb.set("A")
        cb.grid(row=r, column=0, sticky="w", pady=(0,2))

        f2 = ttk.Frame(row_frame); f2.grid(row=r, column=1, sticky="w", padx=(4,0), pady=(0,2))
        press_sb = ttk.Spinbox(f2, from_=10, to=5000, width=6)
        press_sb.set(50); press_sb.pack(side="left")
        ttk.Label(f2, text=" ms", font=("Microsoft YaHei",7)).pack(side="left")

        f3 = ttk.Frame(row_frame); f3.grid(row=r, column=2, sticky="w", padx=(4,0), pady=(0,2))
        interval_sb = ttk.Spinbox(f3, from_=10, to=60000, width=6)
        interval_sb.set(1000); interval_sb.pack(side="left")
        ttk.Label(f3, text=" ms", font=("Microsoft YaHei",7)).pack(side="left")

        f4 = ttk.Frame(row_frame); f4.grid(row=r, column=3, sticky="w", padx=(4,0), pady=(0,2))
        jitter_sb = ttk.Spinbox(f4, from_=0, to=5000, width=6)
        jitter_sb.set(0); jitter_sb.pack(side="left")
        ttk.Label(f4, text=" ms", font=("Microsoft YaHei",7)).pack(side="left")

        btn = ttk.Button(row_frame, text="✕", width=2,
                         command=lambda idx=r: self._remove_key_row(idx))
        btn.grid(row=r, column=4, padx=(4,0), pady=(0,2))

        self._kb_task_rows.append((r, cb, press_sb, interval_sb, jitter_sb))

    def _remove_key_row(self, row_idx):
        for i, (r, *_) in enumerate(self._kb_task_rows):
            if r == row_idx:
                self._kb_task_rows.pop(i)
                break
        # 清除该行的所有 widgets
        for w in self._kb_rows_frame.grid_slaves(row=row_idx):
            w.destroy()

    def _clear_key_rows(self):
        self.keyboarder.stop_all()
        self.keyboarder.clear()
        for r, *_ in self._kb_task_rows:
            for w in self._kb_rows_frame.grid_slaves(row=r):
                w.destroy()
        self._kb_task_rows.clear()
        self._next_row = 1
        self._update_kb_ui()

    def _collect_key_tasks(self):
        tasks = []
        for (_, cb, press_sb, interval_sb, jitter_sb) in self._kb_task_rows:
            try:
                tasks.append(KeyTask(
                    key_name=cb.get(),
                    press_ms=int(float(press_sb.get())),
                    interval_ms=int(float(interval_sb.get())),
                    jitter_ms=int(float(jitter_sb.get())),
                ))
            except (ValueError, tk.TclError):
                pass
        return tasks

    def _toggle_keyboard(self):
        if self.keyboarder.is_running:
            self.keyboarder.stop_all()
        else:
            self.keyboarder.clear()
            for t in self._collect_key_tasks():
                self.keyboarder.add(t)
            self.keyboarder.start_all()
        self._update_kb_ui()

    def _update_kb_ui(self):
        if self.keyboarder.is_running:
            self._kb_start_btn.configure(text="停 止")
            self._kb_status_label.configure(text="运行中", foreground="green")
        else:
            self._kb_start_btn.configure(text="开 始")
            self._kb_status_label.configure(text="已停止", foreground="gray")

    def _kb_poll(self):
        if self.keyboarder.is_running:
            self._kb_count_var.set(str(self.keyboarder.total_count))
        self.root.after(200, self._kb_poll)

    # ================================================================
    # 底部通用栏
    # ================================================================
    def _bottom_bar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(8,0))
        self._top_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="窗口置顶", variable=self._top_var, command=self._toggle_top).pack(side="left")
        ttk.Button(bar, text="重置计数", command=self._reset_count).pack(side="right")

    # ================================================================
    # 鼠标 — 设置同步
    # ================================================================
    def _read_mouse_settings(self):
        self.clicker.interval_ms = float(self._interval_sb.get())
        self.clicker.jitter_ms = float(self._jitter_sb.get())
        self.clicker.press_ms = float(self._press_sb.get())

        type_map = {"左键":"left","右键":"right","中键":"middle"}
        self.clicker.click_type = type_map[self._type_cb.get()]

        send_map = {"标准 (pynput)":"pynput","兼容 (Win32)":"win32"}
        self.clicker.send_mode = send_map[self._send_mode_cb.get()]

        if self._mode_cb.get() == "固定坐标":
            self.clicker.mode = "fixed"
            try:
                self.clicker.set_fixed_position(int(self._x_entry.get()), int(self._y_entry.get()))
            except ValueError:
                pass
        else:
            self.clicker.mode = "follow"

    # ================================================================
    # 鼠标 — 事件处理
    # ================================================================
    def _toggle_mouse(self):
        self._read_mouse_settings()
        self.clicker.toggle()
        if self.clicker.is_running:
            self._start_btn.configure(text="停 止")
            self._status_var.set("运行中")
            self._status_label.configure(foreground="green")
        else:
            self._start_btn.configure(text="开 始")
            self._status_var.set("已停止")
            self._status_label.configure(foreground="gray")

    def _on_mouse_count(self, count):
        self.root.after_idle(lambda: self._count_var.set(str(count)))

    def _on_mode_change(self, event=None):
        state = "normal" if self._mode_cb.get() == "固定坐标" else "disabled"
        self._set_fixed_state(state)

    def _set_fixed_state(self, state):
        for child in self._pos_frame.winfo_children():
            try:
                child.configure(state=state)
            except Exception:
                pass

    def _pick_position(self):
        from pynput.mouse import Controller
        pos = Controller().position
        self._x_entry.delete(0,"end"); self._x_entry.insert(0, str(int(pos[0])))
        self._y_entry.delete(0,"end"); self._y_entry.insert(0, str(int(pos[1])))

    def _pick_position_hotkey(self):
        self.root.after_idle(self._pick_position)

    def _toggle_top(self):
        self.root.attributes("-topmost", self._top_var.get())

    def _reset_count(self):
        self.clicker.reset_count()
        self.keyboarder.clear()
        for t in self._collect_key_tasks():
            self.keyboarder.add(t)
        self._count_var.set("0")
        self._kb_count_var.set("0")

    # ================================================================
    # 热键
    # ================================================================
    def _bind_hotkey(self):
        hotkey = self._hotkey_var.get().strip()
        self._normalize_and_bind(hotkey)
        self.hotkey_mgr.register("<f7>", self._pick_position_hotkey)
        self.hotkey_mgr.register("<f8>", self._kb_hotkey_action)

    def _on_hotkey_change(self, event=None):
        new_hotkey = self._hotkey_var.get().strip()
        if new_hotkey:
            self._normalize_and_bind(new_hotkey)

    def _normalize_and_bind(self, text):
        self.hotkey_mgr.unregister("<f6>")
        parts = text.replace(" ","").lower().split("+")
        converted = []
        for p in parts:
            if p.startswith("f") and p[1:].isdigit():
                converted.append(f"<{p}>")
            elif p in ("ctrl","shift","alt","cmd"):
                converted.append(f"<{p}>")
            else:
                converted.append(p)
        self.hotkey_mgr.register("+".join(converted), self._hotkey_action)

    def _hotkey_action(self):
        self.root.after_idle(self._toggle_mouse)

    def _kb_hotkey_action(self):
        self.root.after_idle(self._toggle_keyboard)

    # ================================================================
    # 生命周期
    # ================================================================
    def shutdown(self):
        self.clicker.stop()
        self.keyboarder.stop_all()
        self.hotkey_mgr.stop()
