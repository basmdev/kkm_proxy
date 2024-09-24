import httpx
from fastapi import FastAPI, Request, HTTPException
from config import TELEGRAM_KEY, KKM_SERVER_URL, CHAT_ID, credentials

app = FastAPI(docs_url=None, redoc_url=None)


# Отправка сообщения в Telegram
async def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


# Запрос к API
async def execute_api_request(data: dict, headers: dict, url: str = KKM_SERVER_URL):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return response.json()


# Проксирование запросов к API
@app.post("/Execute")
async def proxy_request(request: Request):
    request_data = await request.json()
    return await execute_api_request(request_data, credentials)


# Получение списка ККМ
async def list_request():
    request_data = {"Command": "List"}
    return await execute_api_request(request_data, credentials)


# Открытие смены
async def open_shift_request():
    request_data = {"Command": "OpenShift"}
    return await execute_api_request(request_data, credentials)


# Закрытие смены
async def close_shift_request():
    request_data = {"Command": "CloseShift"}
    return await execute_api_request(request_data, credentials)
