from fastapi import APIRouter, Request
from telegram import Update
from ...services.bot import initialize_bot, application
from fastapi import Request, HTTPException

chinedu = APIRouter(prefix="/api/v1", tags=['chinedu'])

chinedu.post("/webhook")
async def telegram_webhook(request: Request):
    await initialize_bot()
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    