"""
物资拾取
"""

import cv2
import numpy as np
import time
from typing import Optional

try:
    import pytesseract
    _HAS_TESSERACT = True
except ImportError:
    _HAS_TESSERACT = False

import movement_control
import key_action


# 物品优先级（越高越优先拾取）
LOOT_PRIORITY: dict[str, int] = {
    # 武器
    "M416": 100, "AKM": 95, "SCAR-L": 90, "M16A4": 85,
    "Kar98k": 95, "M24": 90, "AWM": 100,
    "UMP45": 80, "Vector": 80, "UZI": 75,
    "SKS": 85, "Mini14": 85, "SLR": 88, "MK14": 95,
    "DP-28": 80, "M249": 85,
    # 防具
    "Helmet (3)": 80, "Helmet (2)": 60,
    "Vest (3)": 80, "Vest (2)": 60,
    # 背包
    "Backpack (3)": 70, "Backpack (2)": 50,
    # 医疗
    "First Aid": 75, "Med Kit": 90,
    "Bandage": 40, "Painkiller": 60, "Energy": 65,
    # 弹药
    "5.56mm": 60, "7.62mm": 60, "9mm": 45, ".45 ACP": 45,
    # 配件
    "8x Scope": 85, "6x Scope": 80, "4x Scope": 75,
    "Suppressor": 70, "Compensator": 65,
    "Extended Mag": 70, "QuickDraw Mag": 70,
    "Vertical Grip": 60, "Angled Grip": 60,
    "Cheek Pad": 55, "Tactical Stock": 55,
}


def scan_loot_items(screenshot: np.ndarray) -> list[dict]:
    """扫描地面物资，返回按优先级排序的物品列表"""
    if not _HAS_TESSERACT:
        return []

    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)

    data = pytesseract.image_to_data(
        binary, lang="eng",
        output_type=pytesseract.Output.DICT
    )

    items = []
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue

        # 模糊匹配物品名
        for item_name, priority in LOOT_PRIORITY.items():
            if _fuzzy_match(text, item_name):
                x = data["left"][i] + data["width"][i] // 2
                y = data["top"][i] + data["height"][i] // 2
                items.append({
                    "name": item_name,
                    "pos": (x, y),
                    "priority": priority,
                    "ocr_text": text,
                })
                break

    items.sort(key=lambda i: i["priority"], reverse=True)
    return items


def _fuzzy_match(ocr_text: str, item_name: str) -> bool:
    """模糊匹配 OCR 文本与物品名"""
    ocr_lower = ocr_text.lower()
    item_lower = item_name.lower()
    # 简单包含匹配
    if item_lower in ocr_lower or ocr_lower in item_lower:
        return True
    # 首字母缩写匹配
    return any(
        ocr_lower.startswith(part.lower())
        for part in item_name.split()
    )


def pick_up_item(item: dict) -> None:
    """拾取单个物品"""
    x, y = item["pos"]
    movement_control.move_to(x, y, duration=0.2)
    key_action.interact()
    time.sleep(0.3)


def auto_loot_cycle(screenshot: np.ndarray) -> int:
    """
    自动拾取循环。
    返回拾取物品数
    """
    items = scan_loot_items(screenshot)
    picked = 0

    for item in items[:5]:  # 最多拾取 5 个
        pick_up_item(item)
        picked += 1

    # 拾取完后小范围移动
    if picked > 0:
        movement_control.strafe_left(0.3)

    return picked