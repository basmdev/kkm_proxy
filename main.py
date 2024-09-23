import httpx
from fastapi import FastAPI, Request, HTTPException, Header
from config import TELEGRAM_KEY, KKM_SERVER_URL, CHAT_ID

app = FastAPI(docs_url=None, redoc_url=None)


# Отправка сообщения в Telegram
async def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


# Выполнение запроса к API
@app.post("/Execute")
async def execute_request(request: Request, authorization: str = Header(None)):
    request_data = await request.json()
    headers = {"Authorization": authorization}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                KKM_SERVER_URL, json=request_data, headers=headers
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return response.json()
