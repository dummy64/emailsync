import os
import re
import logging
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread
from config import SPREADSHEET_ID, SHEET_NAME, GMAIL_SEARCH_QUERY, SCOPES, DAYS_TO_FETCH

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

TOKEN_FILE = "token.json"
CREDS_FILE = "credentials.json"


def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info("Refreshing expired token...")
            creds.refresh(Request())
        else:
            log.info("Starting OAuth flow — a browser window will open...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    log.info("Authenticated successfully.")
    return creds


def parse_snippet(snippet):
    def extract(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    name = extract(r"From:\s*(.+?)\s+\S+@\S+", snippet)
    email = extract(r"([\w.\-+]+@[\w.\-]+\.\w+)", snippet)
    phone = extract(r"Phone\s*number:\s*([\d\s\-+]+)", snippet)
    location = extract(r"Message\s*Body:\s*(.+?)(?:Phone|$)", snippet)
    message = extract(r"Message\s*from\s*user:\s*(.+)", snippet)

    return [name, email, phone, location, message]


def get_email_details(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="metadata",
                                          metadataHeaders=["Date"]).execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    snippet = msg.get("snippet", "")
    parsed = parse_snippet(snippet)
    parsed.append(headers.get("Date", ""))
    return parsed


def fetch_admission_emails(service):
    after = (datetime.now() - timedelta(days=DAYS_TO_FETCH)).strftime("%Y/%m/%d")
    query = f'{GMAIL_SEARCH_QUERY} after:{after}'
    log.info(f"Searching Gmail: {query}")
    messages = []
    result = service.users().messages().list(userId="me", q=query, maxResults=500).execute()
    messages.extend(result.get("messages", []))

    while "nextPageToken" in result:
        result = service.users().messages().list(
            userId="me", q=query, maxResults=500,
            pageToken=result["nextPageToken"]
        ).execute()
        messages.extend(result.get("messages", []))

    if not messages:
        log.info("No emails found.")
        return []

    log.info(f"Found {len(messages)} email(s). Extracting details...")
    rows = []
    for i, m in enumerate(messages, 1):
        rows.append(get_email_details(service, m["id"]))
        if i % 10 == 0 or i == len(messages):
            log.info(f"Processed {i}/{len(messages)} emails...")
    return rows


def update_sheet(creds, rows):
    log.info("Connecting to Google Sheet...")
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    if not sheet.row_values(1):
        log.info("Adding headers to sheet...")
        sheet.append_row(["Parent Name", "Email", "Phone Number", "Location", "Message", "Date"],
                         value_input_option="USER_ENTERED")

    existing = sheet.get_all_values()[1:]  # skip header
    existing_keys = {(r[1], r[5]) for r in existing if len(r) > 5}
    new_rows = [r for r in rows if (r[1], r[5]) not in existing_keys]

    if not new_rows:
        log.info("No new emails to add — all already in sheet.")
        return

    log.info(f"Adding {len(new_rows)} new row(s) to the sheet...")
    sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    log.info("Sheet updated successfully.")


def main():
    creds = authenticate()
    gmail = build("gmail", "v1", credentials=creds)
    rows = fetch_admission_emails(gmail)
    if rows:
        update_sheet(creds, rows)
    log.info("Done!")


if __name__ == "__main__":
    main()
