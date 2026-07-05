"""
单实例锁 - 防止重复运行
"""

import os
import sys
import tempfile


def acquire_lock() -> bool:
    """获取单实例锁，返回 True 表示成功获取"""
    if sys.platform == "win32":
        return _acquire_lock_windows()
    else:
        return _acquire_lock_unix()


def _acquire_lock_windows() -> bool:
    try:
        import win32event
        import win32api
        import winerror

        global _mutex
        _mutex = win32event.CreateMutex(None, False, "RuntimeBroker_Instance")
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            return False
        return True
    except ImportError:
        # 降级方案：文件锁
        return _acquire_lock_unix()


def _acquire_lock_unix() -> bool:
    lock_file = os.path.join(tempfile.gettempdir(), "runtime_broker.lock")

    try:
        import fcntl

        global _lock_fd
        _lock_fd = open(lock_file, "w")
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fd.write(str(os.getpid()))
        _lock_fd.flush()
        return True
    except (IOError, OSError, ImportError):
        return False