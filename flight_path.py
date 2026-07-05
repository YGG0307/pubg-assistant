"""
跳伞路径规划
"""

import math
from typing import Optional

# ===== 需要根据实际游戏校准的参数 =====
# 跳伞机制参考：
# - 不开伞垂直下降：约 234 km/h，到达地面约 30 秒
# - 开伞平飞：约 60 km/h，可滑翔约 1.5-2 km
# - 飞机高度：约 1500m
# - 飞机速度：约 140 km/h

PLANE_SPEED = 140.0       # 飞机速度 km/h
PLANE_ALTITUDE = 1500.0   # 飞机高度 m
FREEFALL_SPEED = 234.0    # 垂直下降速度 km/h
GLIDE_SPEED = 60.0        # 平飞速度 km/h
MAX_GLIDE_DIST = 2000.0   # 最大滑翔距离 m
NEAR_JUMP_DIST = 600.0    # 近点跳伞阈值 m


def calculate_jump_distance(target_dist: float) -> float:
    """
    计算最佳跳伞距离。
    target_dist: 目标离飞机的距离（米）
    返回：应该在离目标多远时跳伞（米）
    """
    if target_dist < NEAR_JUMP_DIST:
        # 近点：飞到目标正上方再跳，垂直下降
        return target_dist
    elif target_dist < MAX_GLIDE_DIST:
        # 中距离：提前跳，平飞滑翔
        return max(0.0, target_dist - MAX_GLIDE_DIST * 0.8)
    else:
        # 远点：立即跳伞，尽量滑翔
        return 0.0


def plan_flight_path(target: tuple[float, float],
                     plane_pos: tuple[float, float],
                     plane_angle: float) -> list[tuple[float, float]]:
    """
    规划跳伞飞行路径。
    target: 目标坐标 (x, y)
    plane_pos: 飞机当前位置
    plane_angle: 飞机航向角度
    返回：飞行路径点列表
    """
    # 简化：直线飞向目标
    return [target]


def get_direction(from_pos: tuple[float, float],
                  to_pos: tuple[float, float]) -> float:
    """计算从 from_pos 到 to_pos 的方向角度（度）"""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return math.degrees(math.atan2(dy, dx))


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    """两点距离"""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)