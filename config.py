SPREADSHEET_ID = "1O_iSsIssKkmeHVI4LLiP82xN1GzgXU6RwNJ7asMHAAc"
SHEET_NAME = "Sheet1"
GMAIL_SEARCH_QUERY = 'subject:"Admission enquiry"'
DAYS_TO_FETCH = 2  # fetch emails from last 2 days (buffer for daily runs)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
