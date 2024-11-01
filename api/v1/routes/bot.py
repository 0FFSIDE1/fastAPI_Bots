from fastapi import APIRouter
from starlette.requests import Request
from telegram import Update
import os
from dotenv import load_dotenv
from ...services.bot import get_application

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")

chinedu = APIRouter(prefix="/api/v1", tags=['chinedu'])

@chinedu.post("/webhook")
async def telegram_webhook(request: Request):
    application = await get_application()
    data = await request.json()
    print(f'data: {data}')
    update = Update.de_json(data, application.bot)
    print(update)
    await application.process_update(update)
    return {"status": "ok"}