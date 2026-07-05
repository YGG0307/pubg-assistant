"""
调试工具
"""

import os
import logging
import cv2
import numpy as np
from datetime import datetime
from utils import ensure_dir, timestamp


def setup_logging(debug: bool = False) -> None:
    """配置日志"""
    ensure_dir("logs")
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(
                f"logs/wlpro_{datetime.now():%Y%m%d}.log", encoding="utf-8"
            ),
            logging.StreamHandler(),
        ],
    )


def save_screenshot(screenshot: np.ndarray, label: str = "") -> str:
    """保存调试截图"""
    ensure_dir("debug_screenshots")
    ts = timestamp()
    path = f"debug_screenshots/{ts}_{label}.png"
    cv2.imwrite(path, screenshot)
    logging.debug(f"截图已保存: {path}")
    return path


def draw_detection_box(screenshot: np.ndarray,
                       x: int, y: int, w: int, h: int,
                       label: str = "",
                       color: tuple = (0, 255, 0)) -> np.ndarray:
    """在截图上画检测框"""
    vis = screenshot.copy()
    cv2.rectangle(vis, (x, y), (x + w, y + h), color, 2)
    if label:
        cv2.putText(vis, label, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return vis


def draw_point(screenshot: np.ndarray,
               x: int, y: int,
               label: str = "",
               color: tuple = (0, 0, 255)) -> np.ndarray:
    """在截图上画标记点"""
    vis = screenshot.copy()
    cv2.circle(vis, (x, y), 5, color, -1)
    if label:
        cv2.putText(vis, label, (x + 10, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return vis