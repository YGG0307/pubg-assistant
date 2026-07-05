"""
移动控制 - 键鼠模拟
"""

import time
import math
from typing import Optional

try:
    import pydirectinput
    pydirectinput.FAILSAFE = False
    pydirectinput.PAUSE = 0.01
    _USE_DIRECTINPUT = True
except ImportError:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.01
    _USE_DIRECTINPUT = False
    pydirectinput = pyautogui

try:
    import pytweening
    _HAS_TWEENING = True
except ImportError:
    _HAS_TWEENING = False


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def move_to(x: int, y: int, duration: float = 0.3) -> None:
    """平滑移动到指定坐标"""
    if _HAS_TWEENING and duration > 0:
        start_x, start_y = pydirectinput.position()
        steps = max(1, int(duration * 120))
        for i in range(1, steps + 1):
            t = pytweening.easeInOutQuad(i / steps)
            cur_x = int(start_x + (x - start_x) * t)
            cur_y = int(start_y + (y - start_y) * t)
            pydirectinput.moveTo(cur_x, cur_y)
            _sleep(1 / 120)
    else:
        pydirectinput.moveTo(x, y, duration=duration)


def move_rel(dx: int, dy: int, duration: float = 0.1) -> None:
    """相对移动"""
    pydirectinput.moveRel(dx, dy, duration=duration)


def move_forward(duration: float = 0.5) -> None:
    """向前移动（W）"""
    pydirectinput.keyDown("w")
    _sleep(duration)
    pydirectinput.keyUp("w")


def move_backward(duration: float = 0.5) -> None:
    """向后移动（S）"""
    pydirectinput.keyDown("s")
    _sleep(duration)
    pydirectinput.keyUp("s")


def strafe_left(duration: float = 0.3) -> None:
    """左移（A）"""
    pydirectinput.keyDown("a")
    _sleep(duration)
    pydirectinput.keyUp("a")


def strafe_right(duration: float = 0.3) -> None:
    """右移（D）"""
    pydirectinput.keyDown("d")
    _sleep(duration)
    pydirectinput.keyUp("d")


def sprint(duration: float = 1.0) -> None:
    """冲刺（Shift + W）"""
    pydirectinput.keyDown("shift")
    pydirectinput.keyDown("w")
    _sleep(duration)
    pydirectinput.keyUp("w")
    pydirectinput.keyUp("shift")


def crouch() -> None:
    """蹲下（C）"""
    pydirectinput.press("c")


def prone() -> None:
    """趴下（Z）"""
    pydirectinput.press("z")


def jump() -> None:
    """跳跃（空格）"""
    pydirectinput.press("space")


def rotate_view(degrees: float, duration: float = 0.1) -> None:
    """旋转视角（鼠标水平移动）"""
    # 灵敏度系数，需要根据实际游戏调整
    sensitivity = 10.0
    pixels = int(degrees * sensitivity)
    pydirectinput.moveRel(pixels, 0, duration=duration)


def look_up(degrees: float, duration: float = 0.1) -> None:
    """向上看"""
    sensitivity = 10.0
    pixels = int(-degrees * sensitivity)
    pydirectinput.moveRel(0, pixels, duration=duration)


def look_down(degrees: float, duration: float = 0.1) -> None:
    """向下看"""
    sensitivity = 10.0
    pixels = int(degrees * sensitivity)
    pydirectinput.moveRel(0, pixels, duration=duration)


def move_toward(target_x: int, target_y: int, duration: float = 0.5) -> None:
    """移动到目标方向（旋转视角 + 前进）"""
    cur_x, cur_y = pydirectinput.position()
    dx = target_x - cur_x
    dy = target_y - cur_y
    angle = math.degrees(math.atan2(dy, dx))

    # 假设屏幕中心为前方
    screen_w, screen_h = pydirectinput.size()
    center_x = screen_w // 2
    if target_x > center_x:
        rotate_view(angle * 0.1, 0.1)

    move_forward(duration)