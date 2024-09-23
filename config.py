import os
from dotenv import load_dotenv

load_dotenv()

KKM_SERVER_URL = os.getenv("KKM_SERVER_URL")
TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
CHAT_ID = os.getenv("CHAT_ID")
