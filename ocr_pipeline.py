import os
import json
import traceback
import uuid
from pathlib import Path
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account

# 環境変数からSERVICE_ACCOUNT_INFOを読み込む
SERVICE_ACCOUNT_INFO = json.loads(os.environ.get("SERVICE_ACCOUNT_INFO"))

# 定数（環境によって必要なら変更）
PROJECT_ID = "kindle-ocr-446705"
LOCATION = "us"
PROCESSOR_ID = "be09feeeb889c2b6"


def load_documentai_client():
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO)
    client_options = ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
    return documentai.DocumentProcessorServiceClient(client_options=client_options, credentials=credentials)


def call_ocr_google(image_path: str) -> str:
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


def run_ocr_pipeline(input_filename: str) -> str:
    # フォルダの準備
    input_folder = Path("input")
    output_folder = Path("output")
    input_folder.mkdir(exist_ok=True)
    output_folder.mkdir(exist_ok=True)

    # ファイルの絶対パス
    input_path = input_folder / input_filename

    # 1001-ユーザー名.png のようにリネーム（今回は uuid で固定）
    username = "安部健太郎"
    file_number = 1001  # 単一処理なので固定
    new_filename = f"{file_number}-{username}{input_path.suffix}"
    renamed_path = input_folder / new_filename
    os.rename(input_path, renamed_path)

    # OCR
    text = call_ocr_google(str(renamed_path))

    # テキスト出力
    txt_filename = renamed_path.stem + ".txt"
    txt_path = output_folder / txt_filename
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text.replace("\n", ""))  # 改行を取り除く（必要に応じて）

    # 結合ファイル名
    combined_filename = f"{uuid.uuid4().hex}_全文文字起こし.txt"
    combined_path = output_folder / combined_filename

    # 結合（今回は1ファイルなのでそのままコピー）
    with open(combined_path, "w", encoding="utf-8") as outfile, open(txt_path, "r", encoding="utf-8") as infile:
        outfile.write(infile.read())

    # クリーンアップ（任意：中間ファイル削除）
    os.remove(renamed_path)
    os.remove(txt_path)

    return str(combined_path)

def run_batch_pipeline():
    # input/ → 作成日時で並び替え → リネーム
    folder_path = Path("input")
    output_folder = Path("output")
    folder_path.mkdir(exist_ok=True)
    output_folder.mkdir(exist_ok=True)

    username = "安部健太郎"
    files = sorted(folder_path.glob("*.*"), key=lambda f: f.stat().st_ctime_ns)

    start_number = 1001
    for idx, file in enumerate(files, start=start_number):
        ext = file.suffix
        new_filename = f"{idx}-{username}{ext}"
        file.rename(folder_path / new_filename)

    # OCRして txt 出力
    for file in folder_path.glob("*.*"):
        text = call_ocr_google(str(file))
        txt_path = output_folder / (file.stem + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text.replace("\n", ""))

    # テキストファイルを結合
    txt_files = sorted(output_folder.glob("*.txt"))
    combined_filename = f"{uuid.uuid4().hex}_全文文字起こし.txt"
    combined_path = output_folder / combined_filename
    with open(combined_path, "w", encoding="utf-8") as f:
        for txt_file in txt_files:
            f.write(txt_file.read_text(encoding="utf-8"))

    # クリーンアップ
    for f in folder_path.glob("*"):
        f.unlink()
    for f in txt_files:
        f.unlink()

    return str(combined_path)

