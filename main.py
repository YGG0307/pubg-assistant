"""
微凉Pro - 主入口
PUBG 游戏自动化辅助工具
"""

import time
import logging
from enum import Enum, auto

import numpy as np
from PIL import ImageGrab

import config
import signals
import single_instance
import window_manager
import start_game
import flight_path
import jizhan
import movement_control
import key_action
import loot
import safe_zone
import ocr_region
import end_game
import game_timeout
import error_clicker
import feishu_reporter
import digit_debug


class GameState(Enum):
    IDLE = auto()           # 空闲
    WAITING_MATCH = auto()  # 等待匹配
    LOADING = auto()        # 加载中
    PLANE = auto()          # 飞机上
    JUMPING = auto()        # 跳伞中
    PLAYING = auto()        # 战斗中
    DEAD = auto()           # 已死亡
    GAME_OVER = auto()      # 结算画面
    ERROR = auto()          # 错误


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

        self._setup_events()

    def _setup_events(self) -> None:
        self.bus.on("game:start", self._on_game_start)
        self.bus.on("game:end", self._on_game_end)
        self.bus.on("error:occurred", self._on_error)

    def run(self) -> None:
        """启动主循环"""
        if not single_instance.acquire_lock():
            logging.error("RuntimeBroker 已在运行中")
            return

        logging.info("RuntimeBroker 启动中...")

        # 查找游戏窗口
        self.hwnd = window_manager.find_game_window()
        if not self.hwnd:
            logging.error("未找到游戏窗口，请确保游戏已启动")
            return

        title = window_manager.get_window_title(self.hwnd)
        logging.info(f"已绑定窗口: {title} (hwnd={self.hwnd})")

        # 加载模板
        if not start_game.ensure_start_templates_loaded():
            logging.warning("模板文件未找到，请将模板图片放入 templates/ 目录")

        self._running = True
        self.state = GameState.IDLE

        try:
            self._main_loop()
        except KeyboardInterrupt:
            logging.info("用户退出")
        finally:
            self._running = False

    def _main_loop(self) -> None:
        """主循环 (10 FPS)"""
        while self._running:
            try:
                self._tick()
            except Exception as e:
                logging.error(f"主循环异常: {e}")
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
            logging.info(f"检测到弹窗: {err}")
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

    # ===== 各状态处理 =====

    def _tick_idle(self, screenshot: np.ndarray) -> None:
        """空闲：检测开始按钮"""
        if not self.cfg.auto_start_match:
            return

        hit = start_game.check_start_button(
            screenshot, threshold=self.cfg.threshold
        )
        if hit:
            logging.info(f"检测到开始按钮 ({hit[2]:.2f})")
            self._click(hit[0], hit[1])
            self.state = GameState.WAITING_MATCH
            self.timeout_detector.reset()

    def _tick_waiting(self, screenshot: np.ndarray) -> None:
        """等待匹配完成"""
        # 检测是否进入加载画面
        if self._detect_loading(screenshot):
            self.state = GameState.LOADING
            self.timeout_detector.reset()

    def _tick_loading(self, screenshot: np.ndarray) -> None:
        """加载中：等待进入飞机"""
        if self._detect_plane(screenshot):
            self.state = GameState.PLANE
            logging.info("已进入飞机")
            self.timeout_detector.reset()

    def _tick_plane(self, screenshot: np.ndarray) -> None:
        """飞机上：等待跳伞时机"""
        if not self.cfg.auto_jump:
            return

        # 选择跳点
        target = jizhan.JUMP_POINTS.get(self.cfg.jump_point)
        if target:
            self._target = target
            self.state = GameState.JUMPING
            logging.info(f"跳伞 → {self.cfg.jump_point}")

    def _tick_jumping(self, screenshot: np.ndarray) -> None:
        """跳伞中"""
        # 检测落地
        if self._detect_landed(screenshot):
            self.state = GameState.PLAYING
            self.bus.emit("game:start")
            logging.info("已落地，开始战斗")
            self.timeout_detector.reset()

    def _tick_playing(self, screenshot: np.ndarray) -> None:
        """战斗中"""
        kills = ocr_region.read_kill_count(screenshot)
        alive = ocr_region.read_alive_count(screenshot)

        # 毒圈检测
        if self.cfg.auto_zone:
            zone = safe_zone.detect_safe_zone(screenshot)
            if zone:
                path = safe_zone.plan_escape_path(
                    self._get_position(), zone
                )
                if path:
                    movement_control.move_forward(0.5)

        # 物资拾取
        if self.cfg.auto_loot:
            picked = loot.auto_loot_cycle(screenshot)
            if picked:
                logging.debug(f"拾取 {picked} 件物品")

        # 超时检测
        is_timeout, reason = self.timeout_detector.check(
            screenshot, kills, alive
        )
        if is_timeout:
            logging.warning(f"超时: {reason}")
            game_timeout.handle_timeout()
            self.timeout_detector.reset()

        # 死亡检测
        if end_game.detect_death(screenshot):
            self.state = GameState.DEAD
            self._last_kills = kills
            logging.info(f"已死亡，击杀: {kills}")

        # 保存调试截图
        if self.cfg.save_screenshots and self.cfg.debug_mode:
            digit_debug.save_screenshot(screenshot, "playing")

    def _tick_dead(self, screenshot: np.ndarray) -> None:
        """死亡后等待结算"""
        if end_game.detect_game_over(screenshot):
            self.state = GameState.GAME_OVER

    def _tick_game_over(self, screenshot: np.ndarray) -> None:
        """结算画面"""
        rank = end_game.detect_rank(screenshot)
        self.bus.emit("game:end", rank=rank, kills=self._last_kills)

        if self.cfg.auto_return_lobby:
            end_game.return_to_lobby()
            time.sleep(5)
            self.state = GameState.IDLE
            self.timeout_detector.reset()

    # ===== 辅助方法 =====

    def _capture(self) -> np.ndarray:
        """截取游戏窗口"""
        try:
            if not window_manager.is_foreground(self.hwnd):
                window_manager.bring_to_foreground(self.hwnd)
                time.sleep(0.05)

            rect = window_manager.get_window_rect(self.hwnd)
            return np.array(ImageGrab.grab(bbox=rect))
        except Exception:
            return None

    def _click(self, x: int, y: int) -> None:
        """点击指定坐标"""
        movement_control.move_to(x, y, duration=0.1)
        key_action.press("enter")

    def _get_position(self) -> tuple[float, float]:
        """获取当前人物在屏幕上的位置（屏幕中心）"""
        import pyautogui
        w, h = pyautogui.size()
        return (w / 2, h / 2)

    def _detect_loading(self, screenshot: np.ndarray) -> bool:
        """检测是否进入加载画面"""
        # 加载画面通常是黑屏或特定画面
        mean = np.mean(screenshot)
        return mean < 30  # 画面很暗

    def _detect_plane(self, screenshot: np.ndarray) -> bool:
        """检测是否在飞机上"""
        # 飞机上画面较亮，且通常有特定 UI
        mean = np.mean(screenshot)
        return mean > 80

    def _detect_landed(self, screenshot: np.ndarray) -> bool:
        """检测是否落地"""
        # 落地后画面恢复正常
        mean = np.mean(screenshot)
        return 40 < mean < 200

    # ===== 事件处理 =====

    def _on_game_start(self, **kwargs) -> None:
        if self.cfg.feishu_webhook:
            feishu_reporter.send_game_start(self.cfg.feishu_webhook)

    def _on_game_end(self, rank: int, kills: int, **kwargs) -> None:
        logging.info(f"游戏结束: 排名 #{rank}, 击杀 {kills}")
        if self.cfg.feishu_webhook and self.cfg.notify_game_end:
            feishu_reporter.send_game_end(
                self.cfg.feishu_webhook, rank, kills
            )

    def _on_error(self, error: str, **kwargs) -> None:
        if self.cfg.feishu_webhook and self.cfg.notify_error:
            feishu_reporter.send_error(self.cfg.feishu_webhook, error)


def run_app() -> None:
    """程序入口"""
    cfg = config.load_config()
    digit_debug.setup_logging(debug=cfg.debug_mode)

    app = WeLiPro(cfg)
    app.run()


if __name__ == "__main__":
    run_app()