"""
窗口管理 - 查找/绑定/操作游戏窗口
"""

import time
from typing import Optional


def find_game_window(process_names: list[str] = None,
                     title_keywords: list[str] = None) -> Optional[int]:
    """查找游戏窗口，返回窗口句柄"""
    if process_names is None:
        process_names = ["TslGame.exe", "TslGame_BE.exe"]
    if title_keywords is None:
        title_keywords = ["PUBG", "绝地求生"]

    try:
        import win32gui
        import win32process
        import psutil

        windows = []

        def enum_callback(hwnd, results):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                proc_name = proc.name()
                if proc_name in process_names or \
                   any(kw in title for kw in title_keywords):
                    results.append(hwnd)
            except Exception:
                pass

        win32gui.EnumWindows(enum_callback, windows)
        return windows[0] if windows else None

    except ImportError:
        print("[window_manager] 需要 pywin32 和 psutil")
        return None


def get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    """获取窗口矩形 (left, top, right, bottom)"""
    import win32gui
    return win32gui.GetWindowRect(hwnd)


def get_client_rect(hwnd: int) -> tuple[int, int, int, int]:
    """获取客户区矩形"""
    import win32gui
    return win32gui.GetClientRect(hwnd)


def is_foreground(hwnd: int) -> bool:
    """检查窗口是否在前台"""
    import win32gui
    return win32gui.GetForegroundWindow() == hwnd


def bring_to_foreground(hwnd: int) -> bool:
    """将窗口带到前台"""
    try:
        import win32gui
        import win32con

        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        return True
    except Exception:
        return False


def get_window_title(hwnd: int) -> str:
    """获取窗口标题"""
    import win32gui
    return win32gui.GetWindowText(hwnd)


def list_visible_windows() -> list[tuple[int, str]]:
    """列出所有可见窗口"""
    import win32gui

    windows = []

    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                results.append((hwnd, title))

    win32gui.EnumWindows(enum_callback, windows)
    return windows