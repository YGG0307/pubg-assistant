"""
配置管理
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Config:
    """应用配置"""
    # 游戏设置
    resolution: str = "1920x1080"
    threshold: float = 0.7
    window_title: str = "PUBG"

    # 跳伞
    auto_jump: bool = True
    jump_point: str = "Pochinki"

    # 自动化
    auto_start_match: bool = True
    auto_loot: bool = True
    auto_shoot: bool = False
    auto_zone: bool = True
    auto_return_lobby: bool = True

    # 通知
    feishu_webhook: str = ""
    notify_game_end: bool = True
    notify_error: bool = False

    # 调试
    debug_mode: bool = False
    save_screenshots: bool = False


def load_config(path: str = "config.json") -> Config:
    """加载配置"""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Config(**data)
        except Exception:
            pass
    return Config()


def save_config(config: Config, path: str = "config.json") -> None:
    """保存配置"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2, ensure_ascii=False)