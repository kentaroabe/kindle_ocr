import os
import json
import traceback
import uuid
from pathlib import Path
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account

def load_service_account_info():
    service_account_info = os.environ.get("SERVICE_ACCOUNT_INFO")
    if not service_account_info:
        raise RuntimeError("SERVICE_ACCOUNT_INFO環境変数が設定されていません。")
    return json.loads(service_account_info)

def load_documentai_client():
    credentials = service_account.Credentials.from_service_account_info(load_service_account_info())
    project_id = "kindle-ocr-446705"
    location = "us"
    client_options = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    return documentai.DocumentProcessorServiceClient(client_options=client_options, credentials=credentials)

def call_ocr_google(image_path: str) -> str:
    PROJECT_ID = "kindle-ocr-446705"
    LOCATION = "us"
    PROCESSOR_ID = "be09feeeb889c2b6"
    try:
        client = load_documentai_client()
        name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)
        with open(image_path, "rb") as image:
            image_content = image.read()
        raw_document = documentai.RawDocument(content=image_content, mime_type="image/png")
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        return result.document.text
    except Exception as e:
        print(f"OCRエラー: {e}")
        traceback.print_exc()
        return ""

def run_batch_pipeline(input_dir, username, book_title):
    input_folder = Path(input_dir)
    output_base = Path("output")
    session_id = input_folder.name
    output_folder = output_base / session_id
    output_folder.mkdir(parents=True, exist_ok=True)

    # ★ ファイル名昇順（タイムスタンプ付与で確実にアップロード順＝作成日順）
    files = sorted(input_folder.glob("*.*"), key=lambda f: f.name)
    for idx, file in enumerate(files, start=1):
        ext = file.suffix
        new_filename = f"{idx:04d}{ext}"
        file.rename(input_folder / new_filename)

    # OCRしてtxt出力
    for file in input_folder.glob("*.*"):
        text = call_ocr_google(str(file))
        txt_path = output_folder / (file.stem + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text.replace("\n", ""))

    # テキストファイルを結合
    txt_files = sorted(output_folder.glob("*.txt"))
    combined_filename = f"{book_title}_{username}_{uuid.uuid4().hex}_全文文字起こし.txt"
    combined_path = output_folder / combined_filename
    with open(combined_path, "w", encoding="utf-8") as f:
        for txt_file in txt_files:
            f.write(txt_file.read_text(encoding="utf-8"))

    # 中間ファイルを消す
    for f in input_folder.glob("*"):
        f.unlink()
    for f in txt_files:
        f.unlink()
    input_folder.rmdir()  # 空であれば削除

    return str(combined_path)
