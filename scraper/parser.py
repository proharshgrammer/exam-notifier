"""
parser.py — Extracts notification items from fetched HTML or RSS content.

Each returned item has:
  title       : str   — notification headline
  url         : str   — direct link to the notice/PDF
  exam        : str   — exam name (e.g. "JEE Mains")
  exam_id     : str   — machine-readable id (e.g. "jee_mains")
  category    : str   — exam category (e.g. "Engineering Entrance")
  source_label: str   — e.g. "Official Website – What's New"
  source_url  : str   — the page that was scraped
"""

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


def parse_notifications(raw_content, src_config: dict, exam_config: dict) -> list[dict]:
    """Route to correct parser based on fetch_type."""
    fetch_type = src_config.get("fetch_type", "html_scrape")

    if fetch_type == "rss":
        return _parse_rss(raw_content, src_config, exam_config)
    else:
        return _parse_html(raw_content, src_config, exam_config)


# ── HTML Parser ────────────────────────────────────────────────────────────────

def _parse_html(html: str, src_config: dict, exam_config: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    base_url = src_config.get("base_url", "")
    selector = src_config.get("selector", "a")
    max_items = 10

    results = []
    seen_urls = set()

    for el in soup.select(selector)[:max_items * 3]:  # overfetch, then filter
        title = _clean_text(el.get_text())
        href = el.get("href", "")

        if not title or len(title) < 8:
            continue
        if not href or href in ("#", "javascript:void(0)", ""):
            continue

        full_url = urljoin(base_url, href) if not href.startswith("http") else href

        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        results.append(_build_item(title, full_url, src_config, exam_config))

        if len(results) >= max_items:
            break

    return results


# ── RSS Parser ─────────────────────────────────────────────────────────────────

def _parse_rss(feed, src_config: dict, exam_config: dict) -> list[dict]:
    results = []
    for entry in feed.entries[:10]:
        title = _clean_text(entry.get("title", ""))
        url = entry.get("link", "")
        if not title or not url:
            continue
        results.append(_build_item(title, url, src_config, exam_config))
    return results


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_item(title: str, url: str, src_config: dict, exam_config: dict) -> dict:
    return {
        "title": title,
        "url": url,
        "exam": exam_config["name"],
        "exam_id": exam_config["id"],
        "category": exam_config.get("category", ""),
        "source_label": src_config.get("label", ""),
        "source_url": src_config.get("url", ""),
    }


def _clean_text(text: str) -> str:
    """Normalize whitespace and strip junk from scraped text."""
    text = re.sub(r"\s+", " ", text).strip()
    # Remove common noise like "New" badge text, arrows, etc.
    text = re.sub(r"^(new|updated|hot|important)\s*", "", text, flags=re.IGNORECASE)
    return text
