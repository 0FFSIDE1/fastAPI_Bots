from fastapi import FastAPI, Request, APIRouter
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import json
from dotenv import load_dotenv
from ...services.bot import get_application

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")

chinedu = APIRouter(prefix="/api/v1", tags=['chinedu'])

@chinedu.post("/webhook")
async def telegram_webhook(request: Request):
   
    # Get the application and data from the request
    application = await get_application()
    data = await request.json()
    print(f'Data received from webhook: {data}')

    # Create an Update object from the received data
    update = Update.de_json(data, application.bot)
    print(f'Processed Update: {update}')

    # Process the update through the application
    await application.process_update(update)

    return {"status": "ok"}
   