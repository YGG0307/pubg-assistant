# 微凉Pro

PUBG 游戏自动化辅助工具。基于原版逆向分析重写，Python 3.12 + OpenCV + Tesseract OCR。

## 安装

```bash
pip install -r requirements.txt
```

需要安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) 并配置中文语言包。

## 运行

```bash
# 命令行模式
python main.py

# GUI 设置面板
python menu.py
```

## 功能

| 模块 | 功能 | 说明 |
|------|------|------|
| 开始匹配 | 自动检测大厅"开始"按钮 | OpenCV 模板匹配，支持多分辨率 |
| 跳伞 | 自动跳伞 + 飞行路径规划 | 20 个预设跳点，支持近点/远点策略 |
| 物资拾取 | 自动识别并拾取地面物品 | OCR 识别 + 30+ 物品优先级排序 |
| 跑毒 | 安全区/毒圈检测 | 小地图霍夫圆检测，自动规划跑毒方向 |
| 结算 | 游戏结束自动返回大厅 | 结算画面识别 + 排名 OCR |
| 通知 | 飞书机器人消息推送 | 游戏开始/结束/异常通知 |
| 异常处理 | 卡死检测 + 弹窗处理 | 画面超时检测 + 网络错误弹窗 |

## 目录结构

```
wlpro/
├── main.py              # 入口 + 8 状态主状态机
├── menu.py              # tkinter GUI 设置面板
├── signals.py           # 事件总线（发布/订阅）
├── config.py            # 配置管理（dataclass + JSON）
├── single_instance.py   # 单实例锁（Win32 Mutex）
├── window_manager.py    # 游戏窗口查找/绑定/激活
├── start_game.py        # 模板匹配检测开始按钮
├── flight_path.py       # 跳伞距离计算 + 路径规划
├── jizhan.py            # 20 个跳点坐标 + 策略选择
├── movement_control.py  # WASD 移动 + 平滑鼠标（pytweening）
├── key_action.py        # 20+ 键位映射（射击/换弹/开镜等）
├── loot.py              # 30+ 物品优先级 + OCR 识别拾取
├── safe_zone.py         # 小地图霍夫圆毒圈检测
├── ocr_region.py        # 击杀/存活/排名/倒计时 OCR
├── end_game.py          # 结算画面检测 + 返回大厅
├── game_timeout.py      # 画面卡死 + 数据超时双重检测
├── error_clicker.py     # 弹窗类型识别（网络/踢出/更新）
├── feishu_reporter.py   # 飞书交互式卡片消息
├── digit_debug.py       # 日志 + 截图保存 + 检测框可视化
├── utils.py             # 资源路径 + 时间戳 + 目录创建
├── requirements.txt     # 依赖清单
├── templates/           # 模板图片（开始按钮、结算画面等）
├── config.json          # 配置文件
└── logs/                # 日志目录
```

## 状态机

```
IDLE → WAITING_MATCH → LOADING → PLANE → JUMPING → PLAYING → DEAD → GAME_OVER
  ↑                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
```

## 技术栈

| 类别 | 技术 |
|------|------|
| 图像识别 | OpenCV (cv2.matchTemplate) |
| OCR | Tesseract 5.x + pytesseract |
| 键鼠模拟 | pydirectinput + pynput + pyautogui |
| 平滑移动 | pytweening |
| GUI | tkinter + ttk |
| 进程管理 | psutil + win32gui + win32process |
| 数值计算 | numpy |
| 截图 | Pillow (ImageGrab) |
| 网络 | requests |
| 通知 | 飞书 Webhook (交互式卡片) |

## 配置项

```json
{
  "resolution": "1920x1080",
  "threshold": 0.7,
  "auto_start_match": true,
  "auto_jump": true,
  "jump_point": "Pochinki",
  "auto_loot": true,
  "auto_shoot": false,
  "auto_zone": true,
  "auto_return_lobby": true,
  "feishu_webhook": "",
  "notify_game_end": true,
  "notify_error": false,
  "debug_mode": false,
  "save_screenshots": false
}
```

## 免责声明

本项目仅用于学习、研究和交流。请在遵守相关法律法规及游戏用户协议的前提下使用。