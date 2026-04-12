"""
fetcher.py — Fetches raw content from a URL.
Supports plain HTML scraping and RSS/Atom feeds.
"""

import time
import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

TIMEOUT = 20  # seconds


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_source(url: str, fetch_type: str) -> str | dict:
    """
    Fetch content from a source URL.

    Args:
        url: The URL to fetch.
        fetch_type: One of 'html_scrape', 'rss'

    Returns:
        For html_scrape: raw HTML string
        For rss: parsed feedparser dict
    """
    time.sleep(1)  # Polite delay between requests

    if fetch_type == "rss":
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            raise ValueError(f"Failed to parse RSS feed: {url}")
        return feed

    # Default: html_scrape
    session = _build_session()
    response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text
