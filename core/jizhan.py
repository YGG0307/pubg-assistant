"""
跳点选择
"""

import random
import math
from typing import Optional

# ===== 跳点坐标（屏幕像素坐标，需要根据实际地图校准） =====
# Erangel 地图常见跳点（屏幕坐标，1600x900 窗口为例）
JUMP_POINTS: dict[str, tuple[float, float]] = {
    "Pochinki": (650, 520),
    "School": (580, 480),
    "Rozhok": (600, 450),
    "Military Base": (700, 700),
    "Georgopol": (480, 400),
    "Yasnaya Polyana": (700, 380),
    "Mylta": (750, 550),
    "Novorepnoye": (800, 650),
    "Primorsk": (550, 620),
    "Severny": (620, 320),
    "Lipovka": (680, 400),
    "Gatka": (600, 580),
    "Mylta Power": (720, 600),
    "Ferry Pier": (700, 540),
    "Shelter": (620, 500),
    "Prison": (660, 680),
    "Zharki": (500, 350),
    "Kameshki": (580, 370),
    "Stalber": (550, 350),
}


def get_jump_points() -> dict[str, tuple[float, float]]:
    """返回所有跳点"""
    return dict(JUMP_POINTS)


def select_jump_point(strategy: str = "safe",
                      plane_path: list[tuple[float, float]] = None) -> str:
    """
    选择跳点。
    strategy: "safe" | "hot" | "random"
    plane_path: 飞机航线路径点
    """
    if strategy == "random":
        return random.choice(list(JUMP_POINTS.keys()))

    if plane_path is None:
        return "Pochinki"

    # 按离航线距离排序
    def dist_to_plane(name: str) -> float:
        pt = JUMP_POINTS[name]
        if not plane_path:
            return 0
        # 计算点到航线段的最短距离
        return min(
            _point_to_segment_dist(pt, plane_path[i], plane_path[i + 1])
            for i in range(len(plane_path) - 1)
        )

    if strategy == "safe":
        # 安全策略：选离航线远的（人少）
        return max(JUMP_POINTS, key=dist_to_plane)
    else:
        # 热门策略：选离航线近的
        return min(JUMP_POINTS, key=dist_to_plane)


def _point_to_segment_dist(p: tuple[float, float],
                           a: tuple[float, float],
                           b: tuple[float, float]) -> float:
    """点到线段的最短距离"""
    px, py = p
    ax, ay = a
    bx, by = b

    abx = bx - ax
    aby = by - ay
    if abx == 0 and aby == 0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)

    t = max(0, min(1, ((px - ax) * abx + (py - ay) * aby) / (abx ** 2 + aby ** 2)))
    proj_x = ax + t * abx
    proj_y = ay + t * aby
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)