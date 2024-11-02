from fastapi import Request, APIRouter

from telegram import Update
import os
import json
from dotenv import load_dotenv
from ...services.bot import get_application, process_update
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")

 
chinedu = APIRouter()

@chinedu.post("/webhook")
async def telegram_webhook(request: Request):
    application = await get_application()  # Get the initialized application
    data = await request.json()  # Get JSON data from the request
    update = Update.de_json(data, application.bot)  # Create an Update object
    await process_update(application, update)  # Process the update
    return {"status": "ok"}
