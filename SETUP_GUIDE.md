# 🛠️ Setup Guide — India Exam Tracker
### For non-developers | Everything is free

---

## What you need (all free, one-time setup)

- A **GitHub account** → [github.com](https://github.com) (free)
- A **Google account** (for Sheets)
- **Telegram** on your phone

Total setup time: ~45 minutes

---

## STEP 1 — Create a GitHub Repository

1. Log in to [github.com](https://github.com)
2. Click the **+** button (top right) → **New repository**
3. Name it: `exam-tracker`
4. Make it **Public** (required for free GitHub Pages)
5. Click **Create repository**
6. Upload all the project files you received into this repo
   (drag & drop them in the GitHub interface)

---

## STEP 2 — Set Up Telegram Bot

1. Open Telegram on your phone
2. Search for **@BotFather** (blue tick, official)
3. Send: `/newbot`
4. It will ask for a name → type: `Exam Updates`
5. It will ask for a username → type something like: `MyExamTrackerBot`
6. **Copy the token it gives you** — looks like: `123456789:AAFxxx...`
   This is your **TELEGRAM_BOT_TOKEN**

7. Now search for your new bot in Telegram and **send it any message** (e.g. "hello")

8. Open this URL in your browser (replace YOUR_TOKEN):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
9. Look for `"id":` inside `"chat":` — that number is your **TELEGRAM_CHAT_ID**
   Example: `"chat": {"id": 987654321, ...}` → your ID is `987654321`

---

## STEP 3 — Set Up Google Sheets

### Create the Sheet
1. Go to [sheets.google.com](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it: **Exam Notifications Log**
4. Copy the **Sheet ID** from the URL bar:
   ```
   https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SHEET_ID/edit
   ```
   Save this somewhere.

### Create a Google Cloud Service Account (free)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (click "Select a project" → "New Project") → name it `exam-tracker`
3. In the search bar, search **"Google Sheets API"** → Click Enable
4. Go to **IAM & Admin** → **Service Accounts** → **Create Service Account**
5. Name: `exam-tracker-bot` → Click **Create and Continue** → Done
6. Click on the service account you just created
7. Go to **Keys** tab → **Add Key** → **Create new key** → **JSON** → **Create**
8. A JSON file downloads automatically — **open it and copy ALL the text inside**
   This is your **GOOGLE_SERVICE_ACCOUNT_JSON**

### Share your Sheet with the service account
1. Open your Google Sheet
2. Click **Share** (top right)
3. In the email field, paste the service account email
   (found inside the JSON file, in the `"client_email"` field — looks like `exam-tracker-bot@exam-tracker-xxxxx.iam.gserviceaccount.com`)
4. Set permission to **Editor** → Click **Send**

---

## STEP 4 — Add Secrets to GitHub

1. Go to your GitHub repo → **Settings** tab
2. Left sidebar: **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The token from Step 2 |
| `TELEGRAM_CHAT_ID` | The number from Step 2 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | The full JSON text from Step 3 |
| `GOOGLE_SHEET_ID` | The sheet ID from Step 3 |

---

## STEP 5 — Enable GitHub Pages (Dashboard)

1. In your GitHub repo, go to **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main` | Folder: `/dashboard`
4. Click **Save**
5. After 2-3 minutes, your dashboard will be live at:
   ```
   https://YOUR-USERNAME.github.io/exam-tracker/
   ```

---

## STEP 6 — Test It Manually

1. Go to your repo → **Actions** tab
2. Click **"Exam Tracker – Scrape & Update"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"** (green button)
4. Wait 2-3 minutes → check if:
   - ✅ Telegram received messages
   - ✅ Google Sheet has rows
   - ✅ Dashboard shows cards

---

## After That — It Runs Automatically!

The system runs every 60 minutes on its own.
You don't need to do anything else.

Check your Telegram whenever you get a notification — it means a new exam update was posted.

---

## Adding a New Exam

1. Open `sources.config.json` in your GitHub repo
2. Add a new block (copy the format of an existing exam)
3. Fill in the exam name, website URL, and CSS selector
4. Save/commit the file
5. The next scheduled run will include the new exam

---

## Troubleshooting

| Problem | Fix |
|---|---|
| No Telegram messages | Double-check BOT_TOKEN and CHAT_ID secrets |
| Google Sheet not updating | Make sure you shared the sheet with the service account email |
| Dashboard not loading | Check GitHub Pages is enabled, wait 5 minutes for deploy |
| GitHub Action fails | Go to Actions tab → click the failed run → read the error log |
