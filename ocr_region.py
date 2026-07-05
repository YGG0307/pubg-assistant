"""
OCR 文字识别 - 游戏内信息读取
"""

import cv2
import numpy as np
from typing import Optional

try:
    import pytesseract
    _HAS_TESSERACT = True
except ImportError:
    _HAS_TESSERACT = False


def _preprocess(image: np.ndarray) -> np.ndarray:
    """OCR 预处理：灰度 + 二值化"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return binary


def read_text(image: np.ndarray, lang: str = "eng",
              config: str = "") -> str:
    """通用 OCR"""
    if not _HAS_TESSERACT:
        return ""
    processed = _preprocess(image)
    return pytesseract.image_to_string(processed, lang=lang, config=config).strip()


def read_kill_count(screenshot: np.ndarray) -> int:
    """读取击杀数（屏幕左上角）"""
    region = screenshot[20:55, 50:160]
    text = read_text(region, config="--psm 7 digits")
    try:
        return int(text.strip())
    except ValueError:
        return 0


def read_alive_count(screenshot: np.ndarray) -> int:
    """读取存活人数（屏幕上方居中）"""
    h, w = screenshot.shape[:2]
    region = screenshot[5:40, w // 2 - 50:w // 2 + 50]
    text = read_text(region, config="--psm 7 digits")
    try:
        return int(text.strip())
    except ValueError:
        return 100


def read_zone_timer(screenshot: np.ndarray) -> int:
    """读取毒圈倒计时"""
    h, w = screenshot.shape[:2]
    # 小地图下方的倒计时
    region = screenshot[h - 70:h - 30, w - 280:w - 80]
    text = read_text(region, config="--psm 7 digits")
    try:
        return int(text.strip())
    except ValueError:
        return 60


def read_rank(screenshot: np.ndarray) -> int:
    """读取结算排名"""
    h, w = screenshot.shape[:2]
    region = screenshot[h // 2 - 60:h // 2 + 60, w // 2 - 120:w // 2 + 120]
    text = read_text(region, config="--psm 7")
    import re
    match = re.search(r"#?(\d+)", text)
    return int(match.group(1)) if match else 0


def detect_text_presence(screenshot: np.ndarray, keywords: list[str],
                         lang: str = "chi_sim") -> bool:
    """检测截图中是否包含关键词"""
    text = read_text(screenshot, lang=lang)
    return any(kw in text for kw in keywords)