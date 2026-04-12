# AGENT BRIEFING — India Exam Tracker
## Complete Context for Autonomous Build

---

## 1. Project Summary

Build an automated exam notification tracker for an Indian college counselor.
The system scrapes official exam websites every 60 minutes, detects new notices,
displays them on a web dashboard, logs them to Google Sheets, and sends Telegram alerts.

**Zero cost. Zero subscriptions. All free-tier services.**

---

## 2. User Profile

- Role: College counselor in India (Mathura, UP)
- Use case: Monitors exam notifications to make YouTube videos about updates
- Technical level: Non-developer — the system must run itself once set up
- Constraint: No paid subscriptions or APIs

---

## 3. Complete File Structure

```
exam-tracker/                         ← GitHub repo root
├── README.md
├── sources.config.json               ← Exam sources registry (editable by user)
├── scraper/
│   ├── main.py                       ← Orchestrator, run by GitHub Actions
│   ├── fetcher.py                    ← HTTP / RSS fetcher
│   ├── parser.py                     ← HTML + RSS parser, returns structured items
│   └── requirements.txt
├── notifier/
│   ├── __init__.py
│   ├── telegram_bot.py               ← Telegram message sender
│   └── sheets_logger.py              ← Google Sheets row appender
├── dashboard/
│   └── index.html                    ← Static dashboard, hosted on GitHub Pages
├── data/
│   ├── notifications.json            ← Auto-updated, read by dashboard
│   └── seen_hashes.json             ← Deduplication store
└── .github/
    └── workflows/
        └── scrape.yml                ← Cron job: every 60 minutes
```

---

## 4. Data Contract

### notifications.json (array of objects)

Each notification object MUST have exactly these fields:

```json
{
  "id":           "md5 hash string — unique dedup key",
  "title":        "Human-readable notification headline",
  "url":          "Direct URL to notice or PDF",
  "exam":         "Display name e.g. JEE Mains",
  "exam_id":      "Snake case id e.g. jee_mains",
  "category":     "e.g. Engineering Entrance",
  "source_label": "e.g. Official Website – What's New",
  "source_url":   "The page that was scraped",
  "fetched_at":   "ISO 8601 UTC timestamp e.g. 2025-04-12T08:00:00+00:00"
}
```

### sources.config.json structure

```json
{
  "sources": [
    {
      "id": "jee_mains",
      "name": "JEE Mains",
      "category": "Engineering Entrance",
      "active": true,
      "sources": [
        {
          "label": "Official Website",
          "url": "https://jeemain.nta.ac.in/",
          "fetch_type": "html_scrape",
          "selector": "CSS selector for anchor tags",
          "base_url": "https://jeemain.nta.ac.in"
        }
      ]
    }
  ],
  "settings": {
    "check_interval_minutes": 60,
    "max_notifications_per_source": 10,
    "notify_on_new_only": true,
    "dedup_window_days": 30
  }
}
```

Supported `fetch_type` values: `html_scrape`, `rss`

---

## 5. Scraper Logic (main.py)

```
FOR each active exam in sources.config.json:
  FOR each source URL in that exam:
    1. Fetch raw content (HTML or RSS)
    2. Parse → list of {title, url, ...} items
    3. For each item:
       a. Compute MD5 hash of (title + url)
       b. If hash is in seen_hashes.json → SKIP
       c. Else:
          - Add hash to seen set
          - Add full item to new_notifications list
          - Call send_telegram_alert(item)
          - Call log_to_sheets(item)

IF new_notifications is not empty:
  - Prepend to existing notifications.json
  - Cap at 500 total items
  - Save notifications.json
  - Save seen_hashes.json
  - Git commit & push (done by GitHub Actions step)
```

---

## 6. GitHub Actions Workflow

File: `.github/workflows/scrape.yml`

- Trigger: `schedule` cron `0 * * * *` (every hour) + `workflow_dispatch`
- Permissions: `contents: write`
- Steps:
  1. Checkout repo
  2. Setup Python 3.11
  3. `pip install -r scraper/requirements.txt`
  4. `python scraper/main.py` with secrets injected as env vars
  5. Git add + commit `data/notifications.json` and `data/seen_hashes.json`
  6. Git push

---

## 7. GitHub Secrets Required

The agent must instruct the user to add these in:
`GitHub repo → Settings → Secrets and variables → Actions → New repository secret`

| Secret Name | What it is | How to get it |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot auth token | Message @BotFather → /newbot |
| `TELEGRAM_CHAT_ID` | Your personal chat ID | Visit `api.telegram.org/bot<TOKEN>/getUpdates` after messaging the bot |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON of GCP service account key | GCP Console → IAM → Service Accounts → Create → Download JSON |
| `GOOGLE_SHEET_ID` | Sheet ID from URL | From `docs.google.com/spreadsheets/d/THIS_PART/edit` |

---

## 8. Google Sheets Setup

The sheet must be shared with the service account email (found in the JSON key file) with **Editor** access.

Sheet tab name: `Notifications`

Columns (auto-created by sheets_logger.py if empty):
1. Date & Time
2. Exam
3. Category
4. Notification Title
5. Source Name
6. Source URL
7. Direct Link

---

## 9. Telegram Bot Setup

1. Open Telegram → search `@BotFather`
2. Send `/newbot` → follow prompts → get token
3. Send any message to your new bot
4. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Look for `"chat": {"id": XXXXXXXXX}` — that number is the CHAT_ID

Message format sent per notification:
```
🔔 JEE Mains

📌 [Notification title here]

🔗 [Open Notice] (clickable link)
📂 Source: Official Website – What's New
```

---

## 10. Dashboard (GitHub Pages)

File: `dashboard/index.html`

- Pure HTML + Tailwind CDN (no build step)
- Reads `../data/notifications.json` (relative path works on GitHub Pages)
- Features:
  - Exam filter buttons (one per exam_id)
  - Cards grid showing: exam badge, title, source, time, "View Notice" link
  - "🆕 New" badge for items fetched within last 6 hours
  - Auto-refresh every 10 minutes client-side
  - Last updated timestamp + total count in header

### GitHub Pages Setup
1. Push repo to GitHub
2. Go to repo Settings → Pages
3. Source: Deploy from branch → `main` → `/dashboard` folder
4. Save. Site goes live at: `https://<username>.github.io/<repo-name>/`

---

## 11. Adding a New Exam (User Guide)

The user only needs to edit `sources.config.json`. Add a new block:

```json
{
  "id": "unique_id_no_spaces",
  "name": "Exam Display Name",
  "category": "Category e.g. State Engineering",
  "active": true,
  "sources": [
    {
      "label": "Official Website",
      "url": "https://official-site.gov.in/",
      "fetch_type": "html_scrape",
      "selector": "a",
      "base_url": "https://official-site.gov.in"
    }
  ]
}
```

Then add a filter button in `dashboard/index.html` matching the new `id`.

---

## 12. Parser Strategy Notes

Many Indian government exam websites:
- Have inconsistent HTML structures
- May block scrapers intermittently
- Use NIC hosting (slow, sometimes down)

**Recommended fallback strategy:**
- Try `selector` from config first
- If 0 results found with config selector, also try these generic fallbacks:
  ```python
  FALLBACK_SELECTORS = [
    "table a", ".whatsnew a", ".whats-new a",
    ".notice-board a", ".news-list a", "ul.notice a",
    ".marquee a", "marquee a"
  ]
  ```
- Log selector used to help user tune config

---

## 13. Deduplication Strategy

- Hash = MD5 of `(title.strip().lower() + "|" + url.strip().lower())`
- seen_hashes.json stores these hashes (committed to repo)
- On each run, skip any item whose hash already exists
- Hashes are never deleted — this prevents re-alerting on old notices

---

## 14. Error Handling Principles

- All per-source errors are caught and logged — one bad source must not crash the run
- Telegram and Sheets failures are non-fatal (logged, execution continues)
- Network failures use 3-retry with exponential backoff
- A 1-second polite delay between source requests

---

## 15. Local Testing

```bash
git clone https://github.com/<user>/<repo>.git
cd exam-tracker
pip install -r scraper/requirements.txt

# Set env vars locally (or use a .env file with python-dotenv)
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
export GOOGLE_SHEET_ID="your_sheet_id"

python scraper/main.py
```

Open `dashboard/index.html` in a browser to see results locally.

---

## 16. Cost Summary

| Service | Free Tier | Limit |
|---|---|---|
| GitHub Actions | 2,000 min/month | Well within for 60-min scrapes |
| GitHub Pages | Unlimited | Static site hosting |
| Telegram Bot API | Free forever | No message limits for personal bots |
| Google Sheets API | Free | 300 reads + 300 writes/min |
| GCP Service Account | Free | No cost for Sheets API |

**Total monthly cost: ₹0**
