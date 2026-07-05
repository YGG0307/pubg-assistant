"""
按键操作 - 游戏内功能键
"""

import time

try:
    import pydirectinput as _input
    _input.FAILSAFE = False
    _input.PAUSE = 0.01
except ImportError:
    import pyautogui as _input
    _input.FAILSAFE = False
    _input.PAUSE = 0.01


# ===== 键位映射 =====
KEY = {
    "reload": "r",
    "interact": "f",
    "inventory": "tab",
    "map": "m",
    "crouch": "c",
    "prone": "z",
    "jump": "space",
    "sprint": "shift",
    "walk": "ctrl",
    "free_look": "alt",
    "weapon_1": "1",
    "weapon_2": "2",
    "weapon_3": "3",
    "pistol": "4",
    "grenade": "g",
    "heal": "8",
    "boost": "9",
    "bandage": "7",
    "push_to_talk": "t",
}


def press(key_name: str) -> None:
    """按下并释放一个键"""
    k = KEY.get(key_name, key_name)
    _input.press(k)


def hold(key_name: str, duration: float = 0.5) -> None:
    """按住一个键"""
    k = KEY.get(key_name, key_name)
    _input.keyDown(k)
    time.sleep(duration)
    _input.keyUp(k)


def shoot(duration: float = 0.1) -> None:
    """射击（鼠标左键）"""
    _input.mouseDown()
    if duration > 0:
        time.sleep(duration)
    _input.mouseUp()


def aim(hold: bool = True) -> None:
    """开镜/关镜（鼠标右键）"""
    if hold:
        _input.mouseDown(button="right")
    else:
        _input.click(button="right")


def aim_off() -> None:
    """关镜"""
    _input.mouseUp(button="right")


def reload() -> None:
    """换弹"""
    press("reload")


def interact() -> None:
    """交互（拾取/开门）"""
    press("interact")


def switch_weapon(slot: int = 1) -> None:
    """切换武器 1/2/3"""
    if 1 <= slot <= 3:
        press(f"weapon_{slot}")


def use_medkit() -> None:
    """使用医疗包"""
    press("heal")


def use_boost() -> None:
    """使用能量饮料"""
    press("boost")


def use_bandage() -> None:
    """使用绷带"""
    press("bandage")


def toggle_map() -> None:
    """开关地图"""
    press("map")


def toggle_inventory() -> None:
    """开关背包"""
    press("inventory")


def free_look_on() -> None:
    """自由视角（Alt）"""
    _input.keyDown(KEY["free_look"])


def free_look_off() -> None:
    """关闭自由视角"""
    _input.keyUp(KEY["free_look"])