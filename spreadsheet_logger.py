import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os

# 環境変数からサービスアカウント情報を読み込む
SERVICE_ACCOUNT_INFO = json.loads(os.environ.get("SERVICE_ACCOUNT_INFO"))

# スコープの定義
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 認証とクライアント作成
creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
client = gspread.authorize(creds)

# スプレッドシートURL
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1rFTCzuytTLeNXT45kLQIYKgsrcsGwDz-xgXn4xgA8XU/edit")
worksheet = spreadsheet.sheet1

def add_row(username, number):
    now = datetime.now()
    japanese_datetime = now.strftime('%Y年%m月%d日 %H時%M分%S秒')
    worksheet.append_row([japanese_datetime, username, number])
    print(f"📝 スプレッドシートにログを追加: {username}, {number}")

def is_user_allowed(username: str) -> bool:
    try:
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1rFTCzuytTLeNXT45kLQIYKgsrcsGwDz-xgXn4xgA8XU/edit")
        ws = sheet.worksheet("利用可否")

        records = ws.get_all_records()
        for row in records:
            if row["名前"] == username:
                return str(row["可否"]).strip().upper() == "TRUE"

        return False  # 名前が見つからない場合は許可しない
    except Exception as e:
        print(f"スプレッドシートアクセス失敗: {e}")
        return False  # 安全側で拒否