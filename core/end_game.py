"""
游戏结束处理
"""

import cv2
import numpy as np
import time
import re
from typing import Optional

from core import ocr_region
from core import key_action
from core import movement_control


def detect_game_over(screenshot: np.ndarray) -> bool:
    """检测是否出现结算画面"""
    # 方法1：OCR 检测关键词
    if ocr_region.detect_text_presence(
        screenshot, ["排名", "返回", "结算", "继续"],
        lang="chi_sim"
    ):
        return True

    # 方法2：检测 "返回大厅" 按钮模板
    try:
        import os
        from utils import get_resource_path

        path = get_resource_path("templates/return_lobby.png")
        if os.path.exists(path):
            template = cv2.imread(path)
            if template is not None:
                result = cv2.matchTemplate(
                    screenshot, template, cv2.TM_CCOEFF_NORMED
                )
                if cv2.minMaxLoc(result)[1] > 0.8:
                    return True
    except Exception:
        pass

    return False


def detect_rank(screenshot: np.ndarray) -> int:
    """OCR 识别排名"""
    return ocr_region.read_rank(screenshot)


def return_to_lobby() -> None:
    """返回大厅"""
    # 按 ESC 退出结算画面
    key_action.press("esc")
    time.sleep(1.5)
    key_action.press("esc")
    time.sleep(1.0)

    # 如果有确认弹窗，按 Enter
    key_action.press("enter")
    time.sleep(3.0)


def detect_death(screenshot: np.ndarray) -> bool:
    """检测是否死亡"""
    return ocr_region.detect_text_presence(
        screenshot, ["死亡", "观战", "淘汰", "阵亡"],
        lang="chi_sim"
    )