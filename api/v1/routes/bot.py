from fastapi import APIRouter, Request, BackgroundTasks
import httpx
import requests
from starlette.requests import Request
from telegram import Update
import os
from dotenv import load_dotenv
from ...services.bot import keep_bot_active
from main import lifespan

from ...services.bot import get_application
import asyncio

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


# POST method to trigger the keep-alive background task
@chinedu.post("/keep-alive")
async def trigger_keep_alive(background_tasks: BackgroundTasks):
    """Starts the background task to send keep-alive messages every 3 minutes."""
    background_tasks.add_task(keep_bot_active)  # Start the background task
    return {"status": "Keep-alive messages will be sent every 3 minutes."}