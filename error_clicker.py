"""
错误弹窗处理
"""

import cv2
import numpy as np
import time
from typing import Optional

import key_action


def detect_error_dialog(screenshot: np.ndarray) -> Optional[str]:
    """检测错误弹窗，返回弹窗类型或 None"""
    from ocr_region import detect_text_presence

    error_patterns = [
        ("network_error", ["网络", "连接", "超时", "重试"]),
        ("kicked", ["踢出", "封禁", "断开"]),
        ("update", ["更新", "维护", "新版本"]),
        ("crash", ["崩溃", "错误", "异常"]),
    ]

    for name, keywords in error_patterns:
        if detect_text_presence(screenshot, keywords, lang="chi_sim"):
            return name

    return None


def handle_error_dialog() -> None:
    """处理错误弹窗"""
    # 尝试按 Enter 确认
    key_action.press("enter")
    time.sleep(0.5)

    # 尝试按 ESC 取消
    key_action.press("esc")
    time.sleep(0.5)