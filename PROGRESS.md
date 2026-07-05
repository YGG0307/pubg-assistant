# 开发进度文档

> 微凉Pro 重写版（RuntimeBrokerHost）— 基于原版逆向工程重写
> 仓库：https://github.com/YGG0307/pubg-assistant

---

## 项目概述

PUBG 游戏自动化辅助工具。Python 3.12 + OpenCV + Tesseract OCR + pydirectinput。

原版为 Cython 编译 + UPX 压缩 + VMProtect 保护，源码不可恢复。基于逆向分析提取的模块结构、API 签名、第三方库清单，从头重写。

## 当前进度

### 已完成 ✅

| 模块 | 文件 | 状态 |
|------|------|------|
| 项目结构 | 24 个文件，~2100 行 | ✅ |
| 事件总线 | signals.py | ✅ |
| 配置管理 | config.py | ✅ |
| 单实例锁 | single_instance.py | ✅ |
| 窗口管理 | window_manager.py | ✅ |
| 开始检测 | start_game.py | ✅ |
| 跳伞 | flight_path.py | ✅ |
| 跳点选择 | jizhan.py | ✅ |
| 移动控制 | movement_control.py | ✅ |
| 按键操作 | key_action.py | ✅ |
| 物资拾取 | loot.py | ✅ |
| 安全区检测 | safe_zone.py | ✅ |
| OCR 识别 | ocr_region.py | ✅ |
| 游戏结束 | end_game.py | ✅ |
| 超时处理 | game_timeout.py | ✅ |
| 弹窗处理 | error_clicker.py | ✅ |
| 飞书通知 | feishu_reporter.py | ✅ |
| 调试工具 | digit_debug.py | ✅ |
| 工具函数 | utils.py | ✅ |
| GUI 面板 | menu.py | ✅ |
| 主状态机 | main.py (8 状态) | ✅ |
| 打包配置 | RuntimeBrokerHost.spec | ✅ |

### 未完成 ❌

| 项目 | 说明 |
|------|------|
| 模板图片 | 需要截取 PUBG 的"开始匹配"、"返回大厅"等按钮图片 |
| 坐标校准 | 各模块中的屏幕坐标需要对着实际游戏调试 |
| 颜色阈值 | 毒圈 HSV 范围、OCR 二值化阈值需要实际调试 |
| 鼠标灵敏度 | movement_control.py 中的灵敏度系数需要校准 |
| 跳伞参数 | flight_path.py 中的距离阈值需要实际测试 |
| 实际测试 | 整个项目尚未在 Windows 上实际运行过 |

## 环境要求

- Windows 10/11 64 位
- Python 3.12
- Tesseract OCR（需安装中文语言包）
- PUBG 游戏

## 开发环境搭建

```bash
git clone https://github.com/YGG0307/pubg-assistant.git
cd pubg-assistant
pip install -r requirements.txt
```

## 打包

```bash
pyinstaller RuntimeBrokerHost.spec
# 输出: dist/RuntimeBrokerHost.exe
```

## 关键设计决策

1. **进程名伪装**：打包为 `RuntimeBrokerHost.exe`，Mutex 名 `RuntimeBroker_Instance`，窗口标题"系统设置"
2. **键鼠模拟**：pydirectinput（DirectInput 层）优于 pyautogui（会被反作弊检测）
3. **平滑移动**：pytweening 缓动函数，模拟人类操作
4. **状态机**：8 状态（IDLE→WAITING_MATCH→LOADING→PLANE→JUMPING→PLAYING→DEAD→GAME_OVER）
5. **事件总线**：Signals 发布/订阅模式，模块间解耦
6. **配置**：dataclass + JSON，支持 GUI 和命令行

## 需要调试校准的参数

所有标 `TODO` 或注释说明的数值都需要在 Windows 上对着实际游戏调试：

```
start_game.py:      threshold=0.7（模板匹配阈值）
flight_path.py:     PLANE_SPEED, MAX_GLIDE_DIST 等跳伞参数
jizhan.py:          JUMP_POINTS 坐标（需要对着实际地图校准）
safe_zone.py:       小地图区域坐标、HSV 颜色范围
ocr_region.py:      截图区域坐标（击杀数、存活数位置）
movement_control.py: 鼠标灵敏度系数 sensitivity=10.0
loot.py:            LOOT_PRIORITY 物品优先级
```

## 测试顺序

1. `python menu.py` — GUI 能否打开
2. `python -c "import window_manager; print(window_manager.find_game_window())"` — 找窗口
3. `python -c "import start_game; print(start_game.ensure_start_templates_loaded())"` — 加载模板
4. `python -c "import movement_control; movement_control.move_forward(0.5)"` — 键鼠模拟
5. `python -c "import ocr_region; print(ocr_region.read_text(cv2.imread('test.png')))"` — OCR
6. `python main.py` — 完整流程（需要 PUBG 在运行）

## 参考文档

逆向分析产生的文档在 `YGG0307/WLPro` 仓库：
- REVERSE_ENGINEERING.md — 完整逆向过程记录
- IMPLEMENTATION_GUIDE.md — 各模块实现推断指南

## 下一步

1. 在 Windows 上搭建开发环境
2. 截取模板图片放入 `templates/`
3. 分模块调试校准坐标和阈值
4. 完整流程测试
5. 打包测试