"""
main.py — Entry point for the India Exam Tracker scraper.
Run by GitHub Actions on a schedule (every 60 minutes).
Also runnable locally: python main.py
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from fetcher import fetch_source
from parser import parse_notifications
from notifier.telegram_bot import send_telegram_alert
from notifier.sheets_logger import log_to_sheets

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CONFIG_FILE = ROOT / "sources.config.json"
DATA_FILE = ROOT / "data" / "notifications.json"
SEEN_FILE = ROOT / "data" / "seen_hashes.json"


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_existing_data() -> list:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return []


def load_seen_hashes() -> set:
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_hashes(hashes: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(hashes), f)


def save_notifications(notifications: list):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Keep most recent 500 notifications to keep file small
    notifications = sorted(notifications, key=lambda x: x["fetched_at"], reverse=True)[:500]
    with open(DATA_FILE, "w") as f:
        json.dump(notifications, f, indent=2, ensure_ascii=False)


def make_hash(title: str, url: str) -> str:
    """Deduplicate by hashing title + url together."""
    raw = f"{title.strip().lower()}|{url.strip().lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


def run():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting exam tracker scrape...")

    config = load_config()
    existing = load_existing_data()
    seen_hashes = load_seen_hashes()

    new_notifications = []

    for exam in config["sources"]:
        if not exam.get("active", True):
            continue

        print(f"  → Checking {exam['name']}...")

        for src in exam["sources"]:
            try:
                raw_html = fetch_source(src["url"], src["fetch_type"])
                items = parse_notifications(raw_html, src, exam)

                for item in items:
                    h = make_hash(item["title"], item["url"])
                    if h in seen_hashes:
                        continue  # Already seen

                    seen_hashes.add(h)
                    item["id"] = h
                    item["fetched_at"] = datetime.now(timezone.utc).isoformat()
                    new_notifications.append(item)

                    # Send Telegram alert
                    send_telegram_alert(item)

                    # Log to Google Sheets
                    log_to_sheets(item)

                    print(f"    ✓ NEW: {item['title'][:80]}")

            except Exception as e:
                print(f"    ✗ Error fetching {src['url']}: {e}")

    if new_notifications:
        all_notifications = new_notifications + existing
        save_notifications(all_notifications)
        save_seen_hashes(seen_hashes)
        print(f"\n✅ Done. {len(new_notifications)} new notifications found.")
    else:
        print("\n✅ Done. No new notifications.")


if __name__ == "__main__":
    run()
