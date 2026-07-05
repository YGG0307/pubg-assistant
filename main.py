"""
RuntimeBrokerHost - 主入口
PUBG 游戏自动化辅助工具
"""

import time
import numpy as np
from enum import Enum, auto
from PIL import ImageGrab

from common import config
from common import signals
from common import single_instance
from common import feishu_reporter
from common import logger
from core import window_manager
from core import start_game
from core import flight_path
from core import jizhan
from core import movement_control
from core import key_action
from core import loot
from core import safe_zone
from core import ocr_region
from core import end_game
from core import game_timeout
from core import error_clicker

log = logger.get_logger("main")


class GameState(Enum):
    IDLE = auto()
    WAITING_MATCH = auto()
    LOADING = auto()
    PLANE = auto()
    JUMPING = auto()
    PLAYING = auto()
    DEAD = auto()
    GAME_OVER = auto()
    ERROR = auto()


class WeLiPro:
    """主控制器"""

    def __init__(self, cfg: config.Config):
        self.cfg = cfg
        self.state = GameState.IDLE
        self.hwnd: int = None
        self.bus = signals.bus
        self.timeout_detector = game_timeout.GameTimeoutDetector()
        self._last_kills = 0
        self._running = False
        self._tick_count = 0
        self._game_count = 0
        self._total_kills = 0

        self._setup_events()

    def _setup_events(self) -> None:
        self.bus.on("game:start", self._on_game_start)
        self.bus.on("game:end", self._on_game_end)
        self.bus.on("error:occurred", self._on_error)

    def run(self) -> None:
        """启动主循环"""
        log.info("=" * 50)
        log.info("RuntimeBrokerHost 启动")
        log.info(f"配置: 分辨率={self.cfg.resolution} 阈值={self.cfg.threshold} "
                 f"跳点={self.cfg.jump_point}")

        if not single_instance.acquire_lock():
            log.error("检测到另一个实例已在运行")
            return

        self.hwnd = window_manager.find_game_window()
        if not self.hwnd:
            log.error("未找到游戏窗口，请确保 PUBG 已启动")
            return

        title = window_manager.get_window_title(self.hwnd)
        log.info(f"已绑定游戏窗口: {title} (hwnd={self.hwnd})")

        n_templates = start_game.ensure_start_templates_loaded()
        if not n_templates:
            log.warning("模板文件未找到，请将模板图片放入 templates/ 目录")
        else:
            log.info(f"已加载模板")

        self._running = True
        self._set_state(GameState.IDLE)

        log.info("主循环开始 (10 FPS)")
        try:
            self._main_loop()
        except KeyboardInterrupt:
            log.info("用户退出")
        finally:
            self._running = False
            self._print_summary()

    def _main_loop(self) -> None:
        """主循环 (10 FPS)"""
        while self._running:
            try:
                self._tick()
                self._tick_count += 1
            except Exception as e:
                logger.log_error("main", str(e))
                self.bus.emit("error:occurred", error=str(e))
            time.sleep(0.1)

    def _tick(self) -> None:
        """每帧逻辑"""
        screenshot = self._capture()
        if screenshot is None:
            return

        # 通用：错误弹窗处理
        err = error_clicker.detect_error_dialog(screenshot)
        if err:
            logger.log_detection("error", "弹窗", err)
            logger.log_action("error", "处理弹窗")
            error_clicker.handle_error_dialog()
            return

        if self.state == GameState.IDLE:
            self._tick_idle(screenshot)
        elif self.state == GameState.WAITING_MATCH:
            self._tick_waiting(screenshot)
        elif self.state == GameState.LOADING:
            self._tick_loading(screenshot)
        elif self.state == GameState.PLANE:
            self._tick_plane(screenshot)
        elif self.state == GameState.JUMPING:
            self._tick_jumping(screenshot)
        elif self.state == GameState.PLAYING:
            self._tick_playing(screenshot)
        elif self.state == GameState.DEAD:
            self._tick_dead(screenshot)
        elif self.state == GameState.GAME_OVER:
            self._tick_game_over(screenshot)

    # ===== 状态处理 =====

    def _set_state(self, new_state: GameState) -> None:
        old = self.state.name if self.state else "START"
        self.state = new_state
        logger.log_state_change(old, new_state.name)

    def _tick_idle(self, screenshot: np.ndarray) -> None:
        if not self.cfg.auto_start_match:
            return

        hit = start_game.check_start_button(
            screenshot, threshold=self.cfg.threshold
        )
        if hit:
            logger.log_detection("start", "开始按钮", f"confidence={hit[2]:.2f}")
            self._click(hit[0], hit[1])
            self._set_state(GameState.WAITING_MATCH)
            self.timeout_detector.reset()

    def _tick_waiting(self, screenshot: np.ndarray) -> None:
        if self._detect_loading(screenshot):
            self._set_state(GameState.LOADING)
            self.timeout_detector.reset()

    def _tick_loading(self, screenshot: np.ndarray) -> None:
        if self._detect_plane(screenshot):
            self._set_state(GameState.PLANE)
            self.timeout_detector.reset()

    def _tick_plane(self, screenshot: np.ndarray) -> None:
        if not self.cfg.auto_jump:
            return

        target = jizhan.JUMP_POINTS.get(self.cfg.jump_point)
        if target:
            self._target = target
            self._set_state(GameState.JUMPING)
            logger.log_action("jump", f"跳伞 → {self.cfg.jump_point}")

    def _tick_jumping(self, screenshot: np.ndarray) -> None:
        if self._detect_landed(screenshot):
            self._set_state(GameState.PLAYING)
            self._game_count += 1
            self.bus.emit("game:start")
            self.timeout_detector.reset()

    def _tick_playing(self, screenshot: np.ndarray) -> None:
        kills = ocr_region.read_kill_count(screenshot)
        alive = ocr_region.read_alive_count(screenshot)

        # 每 30 帧记录一次状态
        if self._tick_count % 30 == 0:
            logger.log_game_event("状态", kills=kills, alive=alive)

        # 毒圈检测
        if self.cfg.auto_zone:
            zone = safe_zone.detect_safe_zone(screenshot)
            if zone:
                path = safe_zone.plan_escape_path(
                    self._get_position(), zone
                )
                if path:
                    logger.log_detection("zone", "跑毒", f"距离={path['distance']:.0f}")
                    movement_control.move_forward(0.5)

        # 物资拾取
        if self.cfg.auto_loot:
            picked = loot.auto_loot_cycle(screenshot)
            if picked:
                logger.log_action("loot", f"拾取 {picked} 件物品")

        # 超时检测
        is_timeout, reason = self.timeout_detector.check(
            screenshot, kills, alive
        )
        if is_timeout:
            logger.log_error("timeout", reason)
            game_timeout.handle_timeout()
            self.timeout_detector.reset()

        # 死亡检测
        if end_game.detect_death(screenshot):
            self._set_state(GameState.DEAD)
            self._last_kills = kills
            self._total_kills += kills

        # 调试截图
        if self.cfg.save_screenshots:
            from common import digit_debug
            digit_debug.save_screenshot(screenshot, "playing")

    def _tick_dead(self, screenshot: np.ndarray) -> None:
        if end_game.detect_game_over(screenshot):
            self._set_state(GameState.GAME_OVER)

    def _tick_game_over(self, screenshot: np.ndarray) -> None:
        rank = end_game.detect_rank(screenshot)
        self.bus.emit("game:end", rank=rank, kills=self._last_kills)

        if self.cfg.auto_return_lobby:
            logger.log_action("lobby", "返回大厅")
            end_game.return_to_lobby()
            time.sleep(5)
            self._set_state(GameState.IDLE)
            self.timeout_detector.reset()

    # ===== 辅助方法 =====

    def _capture(self) -> np.ndarray:
        try:
            if not window_manager.is_foreground(self.hwnd):
                window_manager.bring_to_foreground(self.hwnd)
                time.sleep(0.05)
            rect = window_manager.get_window_rect(self.hwnd)
            return np.array(ImageGrab.grab(bbox=rect))
        except Exception as e:
            logger.log_error("capture", str(e))
            return None

    def _click(self, x: int, y: int) -> None:
        movement_control.move_to(x, y, duration=0.1)
        key_action.press("enter")

    def _get_position(self) -> tuple[float, float]:
        import pyautogui
        w, h = pyautogui.size()
        return (w / 2, h / 2)

    def _detect_loading(self, screenshot: np.ndarray) -> bool:
        return np.mean(screenshot) < 30

    def _detect_plane(self, screenshot: np.ndarray) -> bool:
        return np.mean(screenshot) > 80

    def _detect_landed(self, screenshot: np.ndarray) -> bool:
        return 40 < np.mean(screenshot) < 200

    # ===== 事件处理 =====

    def _on_game_start(self, **kwargs) -> None:
        logger.log_game_event("游戏开始", game_count=self._game_count)
        if self.cfg.feishu_webhook:
            feishu_reporter.send_game_start(self.cfg.feishu_webhook)

    def _on_game_end(self, rank: int, kills: int, **kwargs) -> None:
        logger.log_game_event("游戏结束", rank=rank, kills=kills)
        if self.cfg.feishu_webhook and self.cfg.notify_game_end:
            feishu_reporter.send_game_end(
                self.cfg.feishu_webhook, rank, kills
            )

    def _on_error(self, error: str, **kwargs) -> None:
        logger.log_error("main", error)
        if self.cfg.feishu_webhook and self.cfg.notify_error:
            feishu_reporter.send_error(self.cfg.feishu_webhook, error)

    def _print_summary(self) -> None:
        log.info("=" * 50)
        log.info(f"运行结束")
        log.info(f"总帧数: {self._tick_count}")
        log.info(f"游戏局数: {self._game_count}")
        log.info(f"总击杀数: {self._total_kills}")
        log.info(f"最终状态: {self.state.name}")
        log.info("=" * 50)


def run_app() -> None:
    cfg = config.load_config()
    logger.setup_logging(debug=cfg.debug_mode)

    app = WeLiPro(cfg)
    app.run()


if __name__ == "__main__":
    run_app()