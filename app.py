from flask import Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
  
    load_dotenv()  # .env を読み込む

    api_key = os.getenv("test_key")
    debug_mode = os.getenv("DEBUG") == "True"
    return api_key