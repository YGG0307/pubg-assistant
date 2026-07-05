# 微凉Pro

PUBG 游戏自动化辅助工具。

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 目录结构

```
wlpro/
├── main.py              # 入口 + 主循环
├── signals.py           # 事件总线
├── config.py            # 配置管理
├── window_manager.py    # 窗口管理
├── start_game.py        # 开始检测
├── flight_path.py       # 跳伞
├── jizhan.py            # 跳点选择
├── movement_control.py  # 移动控制
├── key_action.py        # 按键操作
├── loot.py              # 物资拾取
├── safe_zone.py         # 安全区检测
├── ocr_region.py        # OCR 识别
├── end_game.py          # 游戏结束
├── game_timeout.py      # 超时处理
├── error_clicker.py     # 弹窗处理
├── feishu_reporter.py   # 飞书通知
├── single_instance.py   # 单实例锁
├── digit_debug.py       # 调试工具
├── utils.py             # 通用工具
├── templates/           # 模板图片
├── config.json          # 配置文件
└── logs/                # 日志
```