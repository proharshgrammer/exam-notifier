# 📋 India Exam Tracker — Project Overview

## What This Project Does

An automated dashboard and notification system for an Indian college counselor to track
exam notifications from multiple official sources — without visiting each site manually.

## Core Features

1. **Web Dashboard** — A clean news-board showing all latest exam notifications, filterable by exam
2. **Google Sheets Log** — Every notification auto-logged with title, exam, timestamp, source URL
3. **Telegram Bot Alerts** — Instant message when new notifications are detected
4. **Scheduled Scraping** — Runs automatically every 30–60 minutes via a free scheduler
5. **Extensible Source Registry** — Add new exam sources easily via a config file

## Exams Tracked (Initial Set)

| Exam | Type |
|------|------|
| JEE Mains | Engineering Entrance |
| JEE Advanced | Engineering Entrance |
| NEET UG | Medical Entrance |
| NEET PG | Medical PG Entrance |
| CUET UG | Central University Entrance |
| CUET PG | Central University PG Entrance |
| WBJEE | West Bengal Engineering |
| MHT-CET | Maharashtra Engineering |
| KCET | Karnataka Engineering |
| AP EAMCET | Andhra Pradesh Engineering |
| TS EAMCET | Telangana Engineering |
| VIT (VITEEE) | VIT University Entrance |
| BITSAT | BITS Pilani Entrance |

> ✅ New exams can be added at any time by editing `sources.config.json` — no code change required.

## Tech Stack (All Free)

| Component | Tool | Cost |
|-----------|------|------|
| Scraping engine | Python + BeautifulSoup / Feedparser | Free |
| Scheduler | GitHub Actions (cron) | Free |
| Dashboard frontend | HTML + Tailwind CSS (static site) | Free |
| Dashboard hosting | GitHub Pages | Free |
| Data storage | JSON flat file in GitHub repo | Free |
| Spreadsheet logging | Google Sheets API (free tier) | Free |
| Telegram notifications | Telegram Bot API | Free forever |
| Secrets management | GitHub Actions Secrets | Free |

## Repository Structure

```
exam-tracker/
├── README.md
├── sources.config.json          ← ADD NEW EXAMS HERE
├── scraper/
│   ├── main.py                  ← Entry point (run by scheduler)
│   ├── fetcher.py               ← HTTP fetch + RSS parsing
│   ├── parser.py                ← Site-specific HTML parsers
│   └── requirements.txt
├── notifier/
│   ├── telegram_bot.py          ← Telegram message sender
│   └── sheets_logger.py         ← Google Sheets writer
├── dashboard/
│   ├── index.html               ← Static dashboard (hosted on GitHub Pages)
│   ├── app.js                   ← Loads notifications.json, renders UI
│   └── style.css
├── data/
│   └── notifications.json       ← Auto-updated by scraper
└── .github/
    └── workflows/
        └── scrape.yml           ← GitHub Actions scheduler
```
