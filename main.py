import httpx
import datetime
import asyncio
from fastapi import FastAPI, Request
from config import (
    TELEGRAM_KEY,
    KKM_SERVER_URL,
    CHAT_ID,
    OPEN_H,
    OPEN_M,
    CLOSE_H,
    CLOSE_M,
    credentials,
)
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    main_task = asyncio.create_task(manage_requests())
    yield
    main_task.cancel()
    await main_task


app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)


# Отправка сообщения в Telegram
async def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


# Запрос к API
async def execute_api_request(data: dict, headers: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(KKM_SERVER_URL, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"Ошибка при выполнении запроса": str(e)}


# Проксирование запросов к API
@app.post("/Execute")
async def proxy_request(request: Request):
    request_data = await request.json()
    return await execute_api_request(request_data, credentials)


# Получение списка ККМ
async def list_request():
    request_data = {"Command": "List"}
    response = await execute_api_request(request_data, credentials)
    devices = response.get("ListUnit", [])
    devices_list = [device["NumDevice"] for device in devices]
    return devices_list


# Открытие смены
async def open_shift_request(num_device: int):
    request_data = {"Command": "OpenShift", "NumDevice": num_device, "NotPrint": True}
    result = await execute_api_request(request_data, credentials)

    device = result.get("NumDevice", "-")
    error = result.get("Error", "-")
    status = result.get("Status", "-")

    await send_to_telegram(
        f"""<b>Открытие смены для ККМ №{device}:</b>
Статус: {status}
Ошибки: {error}"""
    )

    return result


# Закрытие смены
async def close_shift_request(num_device: int):
    request_data = {"Command": "CloseShift", "NumDevice": num_device, "NotPrint": True}
    result = await execute_api_request(request_data, credentials)

    device = result.get("NumDevice", "-")
    error = result.get("Error", "-")
    status = result.get("Status", "-")

    await send_to_telegram(
        f"""<b>Закрытие смены для ККМ №{device}:</b>
Статус: {status}
Ошибки: {error}"""
    )

    return result


# Управление запросами
async def manage_requests():
    while True:
        try:
            now = datetime.datetime.now()

            if now.hour == CLOSE_H and now.minute == CLOSE_M:
                devices = await list_request()
                await asyncio.gather(
                    *(close_shift_request(num_device) for num_device in devices)
                )

            elif now.hour == OPEN_H and now.minute == OPEN_M:
                devices = await list_request()
                await asyncio.gather(
                    *(open_shift_request(num_device) for num_device in devices)
                )

            await asyncio.sleep(60)

        except asyncio.CancelledError:
            break
