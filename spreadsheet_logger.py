import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os

def get_service_account_info():
    service_account_info = os.environ.get("SERVICE_ACCOUNT_INFO")
    if not service_account_info:
        raise RuntimeError("SERVICE_ACCOUNT_INFO環境変数がありません")
    return json.loads(service_account_info)

def get_worksheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(get_service_account_info(), scope)
    client = gspread.authorize(creds)
    spreadsheet_url = os.environ.get("SPREADSHEET_URL")
    if not spreadsheet_url:
        raise RuntimeError("SPREADSHEET_URL環境変数がありません")
    spreadsheet = client.open_by_url(spreadsheet_url)
    return spreadsheet.sheet1

def add_row(username, number):
    try:
        worksheet = get_worksheet()
        now = datetime.now()
        japanese_datetime = now.strftime('%Y年%m月%d日 %H時%M分%S秒')
        worksheet.append_row([japanese_datetime, username, number])
        print(f"📝 スプレッドシートにログを追加: {username}, {number}")
    except Exception as e:
        print(f"スプレッドシートログ追加失敗: {e}")

def is_user_allowed(username):
    # シンプルな実装例（ここを実際のロジックに）
    return True  # 必要なら過去の利用数をチェック
