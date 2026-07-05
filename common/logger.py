"""
日志系统 - 每次运行独立日志文件 + 黑匣子截图
"""

import os
import logging
import traceback
from datetime import datetime
from typing import Optional
from common.utils import ensure_dir


# 本次运行的日志文件路径
_current_log_file: Optional[str] = None
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "RuntimeBroker") -> logging.Logger:
    """获取模块日志"""
    return logging.getLogger(f"RB.{name}")


def setup_logging(debug: bool = False, log_dir: str = "logs") -> str:
    """
    配置日志系统，每次运行创建独立日志文件。
    返回日志文件路径。
    """
    global _logger, _current_log_file
    ensure_dir(log_dir)

    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    _current_log_file = os.path.join(log_dir, f"run_{run_ts}.log")

    _logger = logging.getLogger("RB")
    level = logging.DEBUG if debug else logging.INFO
    _logger.setLevel(logging.DEBUG)  # 文件始终 DEBUG，控制台 INFO

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # 文件日志 — 本次运行专用
    fh = logging.FileHandler(_current_log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    _logger.addHandler(fh)

    # 控制台日志
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    _logger.info(f"日志文件: {_current_log_file}")

    return _current_log_file


def dump_config(cfg_dict: dict) -> None:
    """输出配置信息到日志"""
    log = get_logger("config")
    log.info("=" * 40)
    log.info("配置信息:")
    for k, v in cfg_dict.items():
        if "webhook" in k and v:
            v = v[:30] + "..."  # 隐藏 webhook 完整内容
        log.info(f"  {k}: {v}")
    log.info("=" * 40)


def log_state_change(old_state: str, new_state: str, detail: str = "") -> None:
    """记录状态变更"""
    msg = f"{old_state} -> {new_state}"
    if detail:
        msg += f"  ({detail})"
    get_logger("state").info(msg)


def log_detection(module: str, target: str, detail: str = "") -> None:
    """记录检测结果"""
    msg = f"检测到 {target}"
    if detail:
        msg += f"  [{detail}]"
    get_logger(f"detect.{module}").info(msg)


def log_action(module: str, action: str, detail: str = "") -> None:
    """记录操作"""
    msg = action
    if detail:
        msg += f"  [{detail}]"
    get_logger(f"action.{module}").info(msg)


def log_game_event(event: str, **kwargs) -> None:
    """记录游戏事件"""
    detail = "  ".join(f"{k}={v}" for k, v in kwargs.items())
    get_logger("game").info(f"{event}  {detail}")


def log_error(module: str, error: str, exc_info: bool = False) -> None:
    """记录错误，可选堆栈"""
    if exc_info:
        get_logger(f"error.{module}").error(error, exc_info=True)
    else:
        get_logger(f"error.{module}").error(error)


def log_warning(module: str, msg: str) -> None:
    get_logger(f"warn.{module}").warning(msg)


def get_log_file_path() -> Optional[str]:
    """获取当前日志文件路径"""
    return _current_log_file


# ===== 黑匣子截图 =====
import numpy as np
import cv2
from collections import deque

_blackbox = deque(maxlen=30)  # 保留最近 30 帧
_blackbox_enabled = False


def enable_blackbox(enabled: bool = True) -> None:
    global _blackbox_enabled
    _blackbox_enabled = enabled


def blackbox_feed(screenshot: np.ndarray) -> None:
    """喂入一帧截图"""
    if _blackbox_enabled:
        _blackbox.append(screenshot.copy())


def blackbox_save(label: str = "error") -> list[str]:
    """保存黑匣子截图，返回文件路径列表"""
    if not _blackbox:
        get_logger("blackbox").info(f"黑匣子为空，无截图保存: {label}")
        return []

    ensure_dir("debug_screenshots")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = []
    for i, img in enumerate(_blackbox):
        path = f"debug_screenshots/bb_{ts}_{label}_{i:02d}.png"
        cv2.imwrite(path, img)
        paths.append(path)

    get_logger("blackbox").info(
        f"黑匣子: {label} 共{len(paths)}帧 "
        f"范围: {paths[0]} ~ {paths[-1]}"
    )
    _blackbox.clear()
    return paths


def blackbox_clear() -> None:
    _blackbox.clear()