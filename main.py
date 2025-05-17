from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import shutil
import os

from ocr_pipeline import run_ocr_pipeline

app = FastAPI()

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    os.makedirs("input", exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    input_path = os.path.join("input", filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result_path = run_ocr_pipeline(filename)

    return FileResponse(result_path, filename=os.path.basename(result_path))
