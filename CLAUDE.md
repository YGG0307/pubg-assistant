# CLAUDE.md — 项目上下文

## 项目

微凉Pro 重写版，PUBG 游戏自动化工具。Python 3.12 + OpenCV + Tesseract OCR。

- 仓库：https://github.com/YGG0307/pubg-assistant
- 打包名：RuntimeBrokerHost.exe
- 进程名：RuntimeBrokerHost.exe（伪装系统进程）
- 开发进度：代码框架完成，尚未在 Windows 上实际测试

## 架构

8 状态状态机：IDLE → WAITING_MATCH → LOADING → PLANE → JUMPING → PLAYING → DEAD → GAME_OVER

模块间通过 signals.py 事件总线通信，config.py 管理配置。

## 关键文件

- main.py — 入口 + 主状态机
- menu.py — tkinter GUI
- 详见 PROGRESS.md

## 注意事项

- 所有屏幕坐标、阈值、颜色范围都需要在 Windows 上对着实际 PUBG 调试
- 使用 pydirectinput 而非 pyautogui（游戏级模拟）
- 模板图片尚未准备，需要截取
- 仅在 Windows 上可运行（依赖 win32gui、pydirectinput 等）