"""
通用工具函数
"""

import os
import sys
from datetime import datetime
from typing import Optional


def get_resource_path(relative_path: str) -> str:
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def timestamp() -> str:
    """返回当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def ensure_dir(path: str) -> None:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """限制值在范围内"""
    return max(min_val, min(max_val, value))