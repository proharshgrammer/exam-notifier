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

def _resolve_generic_title(el) -> str:
    """If the link text is a generic 'View PDF' / 'Click Here', walk up the DOM to find a real title."""
    title = el.get_text().strip()
    
    # Generic phrasing check (case-insensitive)
    generic_phrases = {
        "view document", "view announcement", "read more", "click here", 
        "view notice", "download", "download notice", "link", "view",
        "view notice →", "view announcement →", "view document →",
        "read more→", "click here →"
    }
    
    clean_t = re.sub(r"\s+", " ", title).strip().lower()
    
    if not clean_t or clean_t in generic_phrases or len(clean_t) < 8:
        # 1. Try table row sibling TDs (common in Samarth tables)
        tr = el.find_parent("tr")
        if tr:
            tds = tr.find_all("td")
            for td in tds:
                text = td.get_text().strip()
                text_clean = re.sub(r"\s+", " ", text).strip().lower()
                if text_clean and text_clean not in generic_phrases and len(text_clean) > 8:
                    return text
                    
        # 2. Try looking for headings or elements with 'title'/'featured-text' class in ancestors
        for parent in el.parents:
            # Look for headings in this ancestor
            for h in parent.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                h_text = h.get_text().strip()
                h_clean = re.sub(r"\s+", " ", h_text).strip().lower()
                if h_clean and h_clean not in generic_phrases and len(h_clean) > 8:
                    return h_text
            # Look for divs with specific title/featured-text classes
            for div in parent.find_all("div", class_=lambda c: c and any(k in c for k in ["title", "featured-text", "content"])):
                div_text = div.get_text().strip()
                div_clean = re.sub(r"\s+", " ", div_text).strip().lower()
                if div_clean and div_clean not in generic_phrases and len(div_clean) > 8 and len(div_clean) < 200:
                    return div_text
                    
    return title


def _parse_html(html: str, src_config: dict, exam_config: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    base_url = src_config.get("base_url", "")
    selector = src_config.get("selector", "a")
    max_items = 10

    results = []
    seen_urls = set()

    for el in soup.select(selector)[:max_items * 3]:  # overfetch, then filter
        raw_title = _resolve_generic_title(el)
        title = _clean_text(raw_title)
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
