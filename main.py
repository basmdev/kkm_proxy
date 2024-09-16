import os
import httpx
from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()

KKM_SERVER_URL = os.getenv("KKM_SERVER_URL")


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
