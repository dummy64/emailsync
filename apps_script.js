// Deploy this as a Google Apps Script Web App
// 1. Go to https://script.google.com → New Project
// 2. Paste this code → Deploy → New Deployment → Web App
// 3. Execute as: Me, Access: Anyone
// 4. Copy the web app URL and paste it in docs/index.html

var SHEET_ID = "1O_iSsIssKkmeHVI4LLiP82xN1GzgXU6RwNJ7asMHAAc";
var SHEET_NAME = "Sheet1";

function getSheet() {
  return SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
}

function doGet(e) {
  var sheet = getSheet();
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var rows = data.slice(1).map(function(row, i) {
    var obj = { _row: i + 2 };
    headers.forEach(function(h, j) { obj[h] = row[j]; });
    return obj;
  });
  return ContentService.createTextOutput(JSON.stringify(rows)).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var params = JSON.parse(e.postData.contents);
  var sheet = getSheet();
  var row = params.row;
  if (params.status !== undefined) sheet.getRange(row, 7).setValue(params.status);
  if (params.comments !== undefined) sheet.getRange(row, 8).setValue(params.comments);
  return ContentService.createTextOutput(JSON.stringify({ success: true })).setMimeType(ContentService.MimeType.JSON);
}
