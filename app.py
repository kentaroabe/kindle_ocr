from flask import Flask
import os

# 開発環境なら dotenv を読み込む
if os.getenv("FLASK_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello_world():
    api_key = os.getenv("test_key")
    debug_mode = os.getenv("DEBUG") == "True"
    return f"API_KEY: {api_key}, DEBUG: {debug_mode}"
