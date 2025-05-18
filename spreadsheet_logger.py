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
    try:
        worksheet = get_worksheet()  # 1番目のシートを取得
        records = worksheet.get_all_records()
        for row in records:
            if row['名前'] == username:
                if str(row['可否']).strip().upper() == "TRUE":
                    return True
                else:
                    return False
        # ユーザーが見つからなかった場合は利用不可
        return False
    except Exception as e:
        print(f"利用可否判定エラー: {e}")
        # エラー時は安全のため利用不可に
        return False
