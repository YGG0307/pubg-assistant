"""
GUI 界面 - tkinter 设置面板
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from common import config
from core.jizhan import JUMP_POINTS
from core import window_manager


class WeLiProGUI:
    """设置面板"""

    def __init__(self, cfg: Optional[config.Config] = None):
        self.cfg = cfg or config.load_config()
        self.root = tk.Tk()
        self.root.title("微凉Pro")
        self.root.resizable(False, False)

        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 游戏设置
        game_frame = ttk.Frame(notebook)
        notebook.add(game_frame, text="游戏设置")
        self._build_game_tab(game_frame)

        # 自动化
        auto_frame = ttk.Frame(notebook)
        notebook.add(auto_frame, text="自动化")
        self._build_auto_tab(auto_frame)

        # 通知
        notify_frame = ttk.Frame(notebook)
        notebook.add(notify_frame, text="通知")
        self._build_notify_tab(notify_frame)

        # 调试
        debug_frame = ttk.Frame(notebook)
        notebook.add(debug_frame, text="调试")
        self._build_debug_tab(debug_frame)

        # 底部按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Button(btn_frame, text="保存配置",
                   command=self._on_save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="刷新窗口",
                   command=self._on_refresh_windows).pack(side="left", padx=5)

    def _build_game_tab(self, parent: ttk.Frame) -> None:
        row = 0

        # 窗口选择
        ttk.Label(parent, text="游戏窗口:").grid(
            row=row, column=0, sticky="w", pady=5)
        self.window_combo = ttk.Combobox(parent, state="readonly", width=30)
        self.window_combo.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        # 分辨率
        ttk.Label(parent, text="分辨率:").grid(
            row=row, column=0, sticky="w", pady=5)
        self.resolution_combo = ttk.Combobox(
            parent, values=["1920x1080", "2560x1440", "1280x720"],
            state="readonly", width=15
        )
        self.resolution_combo.grid(
            row=row, column=1, sticky="w", pady=5, padx=5)
        row += 1

        # 模板阈值
        ttk.Label(parent, text="模板阈值:").grid(
            row=row, column=0, sticky="w", pady=5)
        self.threshold_scale = ttk.Scale(
            parent, from_=0.5, to=1.0, orient="horizontal"
        )
        self.threshold_scale.grid(
            row=row, column=1, sticky="ew", pady=5, padx=5)
        self.threshold_label = ttk.Label(parent, text="0.70")
        self.threshold_label.grid(row=row, column=2, pady=5)
        self.threshold_scale.configure(
            command=lambda v: self.threshold_label.configure(
                text=f"{float(v):.2f}"
            )
        )
        row += 1

    def _build_auto_tab(self, parent: ttk.Frame) -> None:
        row = 0

        self.auto_start = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动开始匹配",
                        variable=self.auto_start).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        self.auto_jump = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动跳伞",
                        variable=self.auto_jump).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        # 跳点选择
        ttk.Label(parent, text="跳点:").grid(
            row=row, column=0, sticky="w", pady=5)
        self.jump_combo = ttk.Combobox(
            parent, values=list(JUMP_POINTS.keys()),
            state="readonly", width=20
        )
        self.jump_combo.grid(row=row, column=1, sticky="w", pady=5, padx=5)
        row += 1

        self.auto_loot = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动拾取物资",
                        variable=self.auto_loot).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        self.auto_shoot = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动射击（谨慎使用）",
                        variable=self.auto_shoot).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        self.auto_zone = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动跑毒",
                        variable=self.auto_zone).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        self.auto_return = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动返回大厅",
                        variable=self.auto_return).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

    def _build_notify_tab(self, parent: ttk.Frame) -> None:
        row = 0

        ttk.Label(parent, text="飞书 Webhook URL:").grid(
            row=row, column=0, sticky="w", pady=5)
        self.webhook_entry = ttk.Entry(parent, width=40)
        self.webhook_entry.grid(
            row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1

        self.notify_end = tk.BooleanVar()
        ttk.Checkbutton(parent, text="游戏结束通知",
                        variable=self.notify_end).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        self.notify_error = tk.BooleanVar()
        ttk.Checkbutton(parent, text="异常通知",
                        variable=self.notify_error).grid(
            row=row, column=0, sticky="w", pady=3)

    def _build_debug_tab(self, parent: ttk.Frame) -> None:
        row = 0

        self.debug_mode = tk.BooleanVar()
        ttk.Checkbutton(parent, text="调试模式",
                        variable=self.debug_mode).grid(
            row=row, column=0, sticky="w", pady=3)
        row += 1

        self.save_screenshots = tk.BooleanVar()
        ttk.Checkbutton(parent, text="自动保存截图",
                        variable=self.save_screenshots).grid(
            row=row, column=0, sticky="w", pady=3)

    def _load_values(self) -> None:
        """从配置加载 UI 值"""
        # 刷新窗口列表
        self._on_refresh_windows()

        self.resolution_combo.set(self.cfg.resolution)
        self.threshold_scale.set(self.cfg.threshold)
        self.threshold_label.configure(text=f"{self.cfg.threshold:.2f}")

        self.auto_start.set(self.cfg.auto_start_match)
        self.auto_jump.set(self.cfg.auto_jump)
        self.jump_combo.set(self.cfg.jump_point)
        self.auto_loot.set(self.cfg.auto_loot)
        self.auto_shoot.set(self.cfg.auto_shoot)
        self.auto_zone.set(self.cfg.auto_zone)
        self.auto_return.set(self.cfg.auto_return_lobby)

        self.webhook_entry.insert(0, self.cfg.feishu_webhook)
        self.notify_end.set(self.cfg.notify_game_end)
        self.notify_error.set(self.cfg.notify_error)

        self.debug_mode.set(self.cfg.debug_mode)
        self.save_screenshots.set(self.cfg.save_screenshots)

    def _on_save(self) -> None:
        """保存配置"""
        self.cfg.resolution = self.resolution_combo.get()
        self.cfg.threshold = float(self.threshold_scale.get())
        self.cfg.auto_start_match = self.auto_start.get()
        self.cfg.auto_jump = self.auto_jump.get()
        self.cfg.jump_point = self.jump_combo.get()
        self.cfg.auto_loot = self.auto_loot.get()
        self.cfg.auto_shoot = self.auto_shoot.get()
        self.cfg.auto_zone = self.auto_zone.get()
        self.cfg.auto_return_lobby = self.auto_return.get()
        self.cfg.feishu_webhook = self.webhook_entry.get()
        self.cfg.notify_game_end = self.notify_end.get()
        self.cfg.notify_error = self.notify_error.get()
        self.cfg.debug_mode = self.debug_mode.get()
        self.cfg.save_screenshots = self.save_screenshots.get()

        config.save_config(self.cfg)
        messagebox.showinfo("保存成功", "配置已保存")

    def _on_refresh_windows(self) -> None:
        """刷新窗口列表"""
        try:
            windows = window_manager.list_visible_windows()
            titles = [f"{title} (0x{hwnd:X})" for hwnd, title in windows]
            self.window_combo["values"] = titles
            if titles:
                self.window_combo.current(0)
        except Exception:
            pass

    def run(self) -> None:
        """启动 GUI 主循环"""
        self.root.mainloop()


if __name__ == "__main__":
    gui = WeLiProGUI()
    gui.run()