"""
事件总线 - 模块间解耦通信
"""

from collections import defaultdict
from typing import Callable, Any


class SignalBus:
    """简单的事件发布/订阅"""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event: str, handler: Callable[..., None]) -> None:
        """订阅事件"""
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable[..., None]) -> None:
        """取消订阅"""
        if event in self._handlers:
            self._handlers[event].remove(handler)

    def emit(self, event: str, **data: Any) -> None:
        """触发事件"""
        for handler in self._handlers.get(event, []):
            try:
                handler(**data)
            except Exception as e:
                print(f"[SignalBus] 事件 '{event}' 处理异常: {e}")


# 全局实例
bus = SignalBus()


# ===== 事件类型 =====
# game:start        - 游戏开始
# game:end          - 游戏结束 (rank, kills)
# game:jump         - 跳伞阶段
# game:land         - 落地
# game:death        - 死亡
# game:match_found  - 匹配成功
# zone:update       - 毒圈更新 (center, radius)
# zone:shrink       - 毒圈缩小
# loot:found        - 发现物资 (items)
# error:occurred    - 异常 (error)
# error:recovered   - 异常恢复
# state:changed     - 状态变更 (old_state, new_state)