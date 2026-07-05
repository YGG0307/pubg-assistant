"""
超时/卡死处理
"""

import time
import cv2
import numpy as np


class GameTimeoutDetector:
    """游戏超时/卡死检测器"""

    def __init__(self, timeout_seconds: float = 300.0):
        self.timeout = timeout_seconds
        self._last_kills: int = 0
        self._last_alive: int = 100
        self._last_change: float = time.time()
        self._last_screenshot: np.ndarray = None
        self._same_frame_count: int = 0

    def check(self, screenshot: np.ndarray,
              kills: int, alive: int) -> tuple[bool, str]:
        """
        检测是否卡死。
        返回 (is_timeout, reason)
        """
        now = time.time()

        # 检测1：游戏数据长时间不变
        if kills == self._last_kills and alive == self._last_alive:
            elapsed = now - self._last_change
            if elapsed > self.timeout:
                return True, f"数据 {elapsed:.0f}s 未变化 (kills={kills}, alive={alive})"
        else:
            self._last_kills = kills
            self._last_alive = alive
            self._last_change = now

        # 检测2：画面长时间不变（卡加载）
        if self._last_screenshot is not None:
            diff = cv2.absdiff(screenshot, self._last_screenshot)
            mean_diff = np.mean(diff)
            if mean_diff < 5.0:
                self._same_frame_count += 1
                if self._same_frame_count > 600:
                    return True, f"画面 {self._same_frame_count / 10:.0f}s 未变化"
            else:
                self._same_frame_count = 0

        self._last_screenshot = screenshot.copy()
        return False, ""

    def reset(self) -> None:
        """重置检测状态"""
        self._last_change = time.time()
        self._same_frame_count = 0
        self._last_screenshot = None

    def elapsed(self) -> float:
        """距离上次状态变化的时间（秒）"""
        return time.time() - self._last_change


def handle_timeout() -> None:
    """处理卡死：ESC → 返回大厅 → 重新开始"""
    from core import key_action
    import time

    key_action.press("esc")
    time.sleep(2.0)
    key_action.press("esc")
    time.sleep(2.0)
    key_action.press("enter")
    time.sleep(5.0)