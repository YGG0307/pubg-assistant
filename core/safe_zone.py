"""
安全区/毒圈检测
"""

import cv2
import numpy as np
import math
from typing import Optional


def detect_safe_zone(screenshot: np.ndarray) -> Optional[dict]:
    """
    检测小地图上的安全区。
    返回 {"center": (x, y), "radius": r, "next_zone": (x, y)} 或 None
    """
    h, w = screenshot.shape[:2]

    # 小地图区域（右下角，约 220x220 像素，需要根据实际分辨率调整）
    map_x1 = w - 250
    map_y1 = h - 300
    map_x2 = w - 30
    map_y2 = h - 50
    minimap = screenshot[map_y1:map_y2, map_x1:map_x2]

    if minimap.size == 0:
        return None

    # 转 HSV
    hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)

    # 白色圈（安全区边界）
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 40, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    # 蓝色圈（毒圈边界）
    lower_blue = np.array([95, 80, 80])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # 霍夫圆检测
    gray = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT,
        dp=1, minDist=50,
        param1=50, param2=30,
        minRadius=15, maxRadius=100
    )

    if circles is not None and len(circles[0]) >= 2:
        circles = sorted(circles[0], key=lambda c: c[2], reverse=True)
        return {
            "center": (circles[0][0], circles[0][1]),
            "radius": circles[0][2],
            "next_zone": (circles[1][0], circles[1][1]) if len(circles) > 1 else None,
        }

    return None


def plan_escape_path(current_pos: tuple[float, float],
                     safe_zone: dict) -> Optional[dict]:
    """
    规划跑毒路径。
    返回 {"angle": float, "distance": float} 或 None（已在安全区内）
    """
    if safe_zone is None:
        return None

    cx, cy = safe_zone["center"]
    px, py = current_pos
    radius = safe_zone["radius"]

    dx = cx - px
    dy = cy - py
    dist = math.sqrt(dx**2 + dy**2)

    if dist < radius * 0.7:
        return None  # 已在安全区内

    angle = math.degrees(math.atan2(dy, dx))
    return {"angle": angle, "distance": dist}


def is_in_zone(current_pos: tuple[float, float],
               safe_zone: dict) -> bool:
    """检查是否在安全区内"""
    if safe_zone is None:
        return True
    cx, cy = safe_zone["center"]
    px, py = current_pos
    return math.sqrt((cx - px)**2 + (cy - py)**2) <= safe_zone["radius"]