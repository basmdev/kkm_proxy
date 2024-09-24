import os
import base64
from dotenv import load_dotenv

load_dotenv()

KKM_SERVER_URL = os.getenv("KKM_SERVER_URL")
TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
CHAT_ID = os.getenv("CHAT_ID")
AUTH_LOGIN = os.getenv("AUTH_LOGIN")
AUTH_PASS = os.getenv("AUTH_PASS")

# Подготовка данных для авторизации
login_data = f"{AUTH_LOGIN}:{AUTH_PASS}"
encoded_data = base64.b64encode(login_data.encode("utf-8")).decode("utf-8")
credentials = {"Authorization": f"Basic {encoded_data}"}
