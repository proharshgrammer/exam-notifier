"""
telegram_bot.py — Sends Telegram messages when new notifications are found.

Setup (one-time):
1. Message @BotFather on Telegram → /newbot → get your BOT_TOKEN
2. Message your bot once (so it can find your chat_id)
3. Visit: https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   Find your chat_id in the response.
4. Add BOT_TOKEN and TELEGRAM_CHAT_ID as GitHub Actions Secrets.

Environment variables required:
  TELEGRAM_BOT_TOKEN  — e.g. "123456789:AAF..."
  TELEGRAM_CHAT_ID    — e.g. "987654321" (your personal chat ID or a group/channel ID)
"""

import os
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram_alert(item: dict) -> bool:
    """
    Send a formatted Telegram message for a new notification.

    Returns True on success, False on failure (non-fatal).
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("    [Telegram] Skipped — BOT_TOKEN or CHAT_ID not set.")
        return False

    # Telegram supports MarkdownV2 — escape special chars
    title = _escape_md(item["title"])
    exam = _escape_md(item["exam"])
    source = _escape_md(item.get("source_label", ""))
    url = item["url"]

    message = (
        f"🔔 *{exam}*\n\n"
        f"📌 {title}\n\n"
        f"🔗 [Open Notice]({url})\n"
        f"📂 Source: {source}"
    )

    try:
        resp = requests.post(
            TELEGRAM_API.format(token=BOT_TOKEN),
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"    [Telegram] Failed to send message: {e}")
        return False


def _escape_md(text: str) -> str:
    """Escape Telegram MarkdownV2 special characters."""
    # For parse_mode=Markdown (v1), fewer escapes needed
    return text.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
