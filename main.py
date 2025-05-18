from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from typing import List
import os
import uuid
import shutil
from datetime import datetime

from ocr_pipeline import run_batch_pipeline
from spreadsheet_logger import add_row, is_user_allowed

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.post("/ocr/batch")
async def ocr_batch(
    files: List[UploadFile] = File(...),
    username: str = Form(...),
    book_title: str = Form(...)
):
    # 利用可否チェック
    if not is_user_allowed(username):
        return JSONResponse(status_code=403, content={
            "message": f"{username} は利用上限に達しています。処理を中止しました。"
        })

    # サブディレクトリでユーザーごとに分離
    session_id = str(uuid.uuid4())
    input_dir = os.path.join("input", session_id)
    os.makedirs(input_dir, exist_ok=True)

    uploaded_paths = []
    for file in files:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f") # マイクロ秒単位
        filename = f"{timestamp}_{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        path = os.path.join(input_dir, filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_paths.append(path)

    # OCR実行
    try:
        result_path = run_batch_pipeline(input_dir, username, book_title)
    except Exception as e:
        shutil.rmtree(input_dir, ignore_errors=True)
        return JSONResponse(status_code=500, content={"message": f"OCRエラー: {str(e)}"})

    # スプレッドシートに処理件数を記録
    add_row(username, len(files))

    # inputサブディレクトリを消す
    shutil.rmtree(input_dir, ignore_errors=True)

    # 処理結果ファイルを返す
    return FileResponse(result_path, filename=os.path.basename(result_path))
