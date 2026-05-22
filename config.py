import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
    GOOGLE_FOLDER_ID = os.getenv("GOOGLE_FOLDER_ID", "YOUR_FOLDER_ID")
    PAYMENT_ACCOUNT = os.getenv("PAYMENT_ACCOUNT", "YOUR_ACCOUNT")
    # и т.д.
