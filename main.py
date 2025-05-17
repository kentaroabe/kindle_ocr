from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
import shutil

from ocr_pipeline import run_batch_pipeline
from spreadsheet_logger import add_row  # ← あなたの元コードのロガー関数

app = FastAPI()

@app.post("/ocr/batch")
async def ocr_batch(
    files: List[UploadFile] = File(...),
    username: str = Form(...),
    book_title: str = Form(...)
):
    input_dir = "input"
    os.makedirs(input_dir, exist_ok=True)

    uploaded_paths = []
    for file in files:
        filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        path = os.path.join(input_dir, filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_paths.append(filename)

    # OCR実行
    result_path = run_batch_pipeline()

    # ログをGoogleスプレッドシートに追加
    add_row(username, len(files))

    return FileResponse(result_path, filename=os.path.basename(result_path))
