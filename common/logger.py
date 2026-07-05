"""
日志系统 - 结构化日志 + 模块日志
"""

import os
import logging
import logging.handlers
from datetime import datetime
from common.utils import ensure_dir


# 全局日志实例
_logger: logging.Logger = None


def get_logger(name: str = "RuntimeBroker") -> logging.Logger:
    """获取模块日志"""
    return logging.getLogger(f"RuntimeBroker.{name}")


def setup_logging(debug: bool = False, log_dir: str = "logs") -> None:
    """配置日志系统"""
    global _logger
    ensure_dir(log_dir)

    _logger = logging.getLogger("RuntimeBroker")
    level = logging.DEBUG if debug else logging.INFO
    _logger.setLevel(level)

    # 格式
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-5s] %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # 文件日志（按天轮转，保留 7 天）
    fh = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, f"log_{datetime.now():%Y%m%d}.log"),
        when="midnight", backupCount=7, encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    _logger.addHandler(fh)

    # 控制台日志
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    _logger.info("日志系统初始化完成")


def log_state_change(old_state: str, new_state: str) -> None:
    """记录状态变更"""
    get_logger("state").info(f"{old_state} -> {new_state}")


def log_detection(module: str, result: str, detail: str = "") -> None:
    """记录检测结果"""
    msg = f"{result}"
    if detail:
        msg += f" | {detail}"
    get_logger(f"detect.{module}").debug(msg)


def log_action(module: str, action: str, detail: str = "") -> None:
    """记录操作"""
    msg = f"{action}"
    if detail:
        msg += f" | {detail}"
    get_logger(f"action.{module}").info(msg)


def log_error(module: str, error: str) -> None:
    """记录错误"""
    get_logger(f"error.{module}").error(error)


def log_game_event(event: str, **kwargs) -> None:
    """记录游戏事件"""
    detail = " ".join(f"{k}={v}" for k, v in kwargs.items())
    get_logger("game").info(f"{event} {detail}")