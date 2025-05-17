from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
import shutil

from ocr_pipeline import run_batch_pipeline

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.post("/ocr/batch")
async def ocr_batch(files: List[UploadFile] = File(...)):
    input_dir = "input"
    os.makedirs(input_dir, exist_ok=True)

    uploaded_paths = []
    for file in files:
        filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        path = os.path.join(input_dir, filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_paths.append(filename)

    result_path = run_batch_pipeline()  # 一括処理関数を呼ぶ
    return FileResponse(result_path, filename=os.path.basename(result_path))
