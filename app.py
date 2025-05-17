from flask import Flask
import os


s

# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import shutil
import os

from your_module import run_ocr_pipeline  # 既存処理を関数化してここから呼ぶ

# 開発環境なら dotenv を読み込む
if os.getenv("FLASK_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)


app = FastAPI()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    input_path = f"input/{filename}"

    # 保存
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 処理開始
    result_path = run_ocr_pipeline(filename)

    return FileResponse(result_path, filename=os.path.basename(result_path))


@app.get("/")
def hello_world():
    api_key = os.getenv("test_key")
    debug_mode = os.getenv("DEBUG") == "True"
    return f"API_KEY: {api_key}, DEBUG: {debug_mode}"