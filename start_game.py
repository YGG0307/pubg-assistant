"""
游戏开始检测 - 模板匹配识别开始按钮
"""

import os
import cv2
import numpy as np
from typing import Optional
from utils import get_resource_path


# 模板缓存
_templates: dict[str, np.ndarray] = {}


def _load_templates() -> dict[str, np.ndarray]:
    """加载所有开始检测模板"""
    global _templates
    if _templates:
        return _templates

    template_defs = {
        "kaishipipei": "templates/kaishipipei.png",
        "start": "templates/start-kashi.png",
        "bugei_start": "templates/bugei-start1.png",
        "bugei_confirm": "templates/bugei-start-queren.png",
    }

    for name, rel_path in template_defs.items():
        path = get_resource_path(rel_path)
        if os.path.exists(path):
            img = cv2.imread(path)
            if img is not None:
                _templates[name] = img

    # 加载航线模板
    for subdir in ["templates/hangxian", "templates/1920-1080/hangxian"]:
        dir_path = get_resource_path(subdir)
        if os.path.isdir(dir_path):
            for fname in sorted(os.listdir(dir_path)):
                if fname.startswith("start-") and fname.endswith(".png"):
                    path = os.path.join(dir_path, fname)
                    img = cv2.imread(path)
                    if img is not None:
                        _templates[f"hangxian/{fname}"] = img

    return _templates


def find_template_in_region(screenshot: np.ndarray,
                            template_path: str,
                            threshold: float = 0.7) -> Optional[tuple[float, float, float]]:
    """在截图中搜索模板，返回 (x, y, confidence) 或 None"""
    template = cv2.imread(template_path)
    if template is None:
        return None

    h, w = template.shape[:2]
    if h > screenshot.shape[0] or w > screenshot.shape[1]:
        return None

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y, max_val)

    return None


def check_start_button(screenshot: np.ndarray,
                       threshold: float = 0.7) -> Optional[tuple[float, float, float]]:
    """检测开始按钮，返回匹配位置或 None"""
    templates = _load_templates()

    for name, template in templates.items():
        h, w = template.shape[:2]
        if h > screenshot.shape[0] or w > screenshot.shape[1]:
            continue

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y, max_val)

    return None


def ensure_start_templates_loaded() -> bool:
    """确保模板已加载"""
    return len(_load_templates()) > 0