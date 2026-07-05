"""
飞书通知
"""

import requests
from datetime import datetime
from typing import Optional


def send_message(webhook: str, title: str, content: str,
                 color: str = "blue") -> bool:
    """发送飞书交互式卡片消息"""
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color,
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content},
                },
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"RuntimeBroker · {datetime.now():%Y-%m-%d %H:%M:%S}",
                        }
                    ],
                },
            ],
        },
    }

    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def send_game_start(webhook: str) -> bool:
    """通知游戏开始"""
    return send_message(webhook, "🎮 游戏开始", "已进入游戏", "blue")


def send_game_end(webhook: str, rank: int, kills: int) -> bool:
    """通知游戏结束"""
    emoji = "🏆" if rank == 1 else "✅" if rank <= 10 else "❌"
    return send_message(
        webhook,
        f"{emoji} 游戏结束",
        f"排名：**#{rank}**\n击杀：**{kills}**",
        "green" if rank <= 10 else "red",
    )


def send_error(webhook: str, error: str) -> bool:
    """通知异常"""
    return send_message(webhook, "⚠️ 异常", error, "red")