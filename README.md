# Email Sync — Admission Enquiry Tracker

Searches Gmail for emails with subject "Admission enquiry" and logs them to a Google Sheet.

## Setup

### 1. Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Gmail API** and **Google Sheets API**
4. Go to **Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Choose "Desktop app", download the JSON and save it as `credentials.json` in this folder

### 2. Google Sheet
1. Create a Google Sheet
2. Add these headers in row 1: `From`, `Subject`, `Date`, `Snippet`
3. Copy the spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit`
4. Paste it into `config.py` as `SPREADSHEET_ID`

### 3. Install & Run
```bash
pip install -r requirements.txt
python email_sync.py
```

On first run, a browser window opens for Google OAuth. After authorizing, a `token.json` file is saved for future runs.

---

## Dashboard (GitHub Pages)

A web dashboard to view and manage enquiries — with click-to-call, status tracking, and comments.

### 1. Add columns to your Google Sheet
Add these headers in row 1 (columns G and H): `Status`, `Comments`

### 2. Deploy the Apps Script API
1. Go to [Google Apps Script](https://script.google.com/) → New Project
2. Paste the contents of `apps_script.js`
3. Update `SHEET_ID` if different from the default
4. Click **Deploy → New Deployment → Web App**
5. Set: Execute as **Me**, Access **Anyone**
6. Copy the deployed URL

### 3. Configure the dashboard
1. Open `docs/index.html`
2. Paste your Apps Script URL into the `API_URL` variable at the top of the `<script>` section

### 4. Enable GitHub Pages
1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Source: **Deploy from a branch**, Branch: `main`, Folder: `/docs`
4. Your dashboard will be live at `https://<username>.github.io/<repo-name>/`
