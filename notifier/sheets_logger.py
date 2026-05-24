"""
sheets_logger.py — Appends new notifications to a Google Sheet.

Setup (one-time):
1. Go to https://console.cloud.google.com/
2. Create a new project (free).
3. Enable "Google Sheets API" for the project.
4. Go to IAM → Service Accounts → Create Service Account.
5. Download the JSON key file.
6. Copy the entire JSON content and add as GitHub Secret: GOOGLE_SERVICE_ACCOUNT_JSON
7. Create a new Google Sheet.
8. Share it (Editor access) with the service account email from the JSON.
9. Copy the Sheet ID from its URL:
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
10. Add as GitHub Secret: GOOGLE_SHEET_ID

Environment variables required:
  GOOGLE_SERVICE_ACCOUNT_JSON  — full JSON string of service account key
  GOOGLE_SHEET_ID              — the spreadsheet ID from the URL
"""

import json
import os
from datetime import datetime, timezone

SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")

# Sheet columns (in order)
COLUMNS = ["Date & Time", "Exam", "Category", "Notification Title", "Source Name", "Source URL", "Direct Link"]

# Name of the sheet/tab to write to
SHEET_TAB = "Notifications"


def log_to_sheets(item: dict) -> bool:
    """
    Appends one row to the configured Google Sheet.
    Returns True on success, False on failure (non-fatal).
    """
    if not SHEET_ID or not SERVICE_ACCOUNT_JSON:
        print("    [Sheets] Skipped — SHEET_ID or SERVICE_ACCOUNT_JSON not set.")
        return False

    try:
        import google.oauth2.service_account as sa
        import googleapiclient.discovery as discovery

        creds_info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = sa.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = discovery.build("sheets", "v4", credentials=creds, cache_discovery=False)

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        row = [
            now,
            item.get("exam", ""),
            item.get("category", ""),
            item.get("title", ""),
            item.get("source_label", ""),
            item.get("source_url", ""),
            item.get("url", ""),
        ]

        # Ensure tab exists and write header
        _ensure_sheet_tab_exists(service)
        _ensure_header(service)

        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_TAB}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute()

        return True

    except Exception as e:
        print(f"    [Sheets] Failed to log: {e}")
        err_str = str(e)
        
        # Diagnostic assistance for users
        client_email = "your-service-account-email"
        try:
            client_email = json.loads(SERVICE_ACCOUNT_JSON).get("client_email", client_email)
        except Exception:
            pass
            
        if "403" in err_str or "permission" in err_str.lower():
            print(f"    👉 TROUBLESHOOTING: Access Denied (403). Ensure you shared the Google Sheet with the Service Account email: '{client_email}' as an 'Editor'.")
        elif "404" in err_str or "requested entity was not found" in err_str.lower():
            print(f"    👉 TROUBLESHOOTING: Spreadsheet Not Found (404). Check if the GOOGLE_SHEET_ID secret is exactly correct.")
        elif "API key not valid" in err_str or "invalid credentials" in err_str.lower():
            print(f"    👉 TROUBLESHOOTING: Authentication failed. Verify that GOOGLE_SERVICE_ACCOUNT_JSON secret is a valid GCP key JSON.")
        return False


def _ensure_sheet_tab_exists(service):
    """Check if the sheet/tab exists, and create it if it does not."""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        sheet_titles = [s['properties']['title'] for s in spreadsheet.get('sheets', [])]
        if SHEET_TAB not in sheet_titles:
            print(f"    [Sheets] Creating missing tab '{SHEET_TAB}'...")
            body = {
                'requests': [
                    {
                        'addSheet': {
                            'properties': {
                                'title': SHEET_TAB
                            }
                        }
                    }
                ]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
    except Exception as e:
        # Pass and let _ensure_header fail if it is a major connection error
        pass


def _ensure_header(service):
    """Write header row if the sheet is empty."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_TAB}!A1:G1",
    ).execute()

    if not result.get("values"):
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_TAB}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [COLUMNS]},
        ).execute()
