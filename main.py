import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api.v1.routes.bot import chinedu
import uvicorn
import requests
from api.services.bot import initialize_bot
load_dotenv()

from fastapi import APIRouter, Request
from telegram import Update
from api.services.bot import initialize_bot, application
from fastapi import Request, HTTPException


bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
webhook_url = os.getenv('WEBHOOK_URL')
print(bot_token, chat_id, webhook_url)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Sets the webhook for the Telegram bot."""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})

    if response.status_code == 200:
        print("Webhook set successfully!")
    else:
        print(f"Failed to set webhook: {response.json()}")

    await initialize_bot()
    print("successful initialization")
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
    "https://405a-197-211-61-7.ngrok-free.app/api/v1/webhook",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chinedu)

@app.get("/")
async def root():
    return {"message": "Welcome to the Telegram Bot Webhook!"}


if __name__ == "__main__":
    # Start the application with uvicorn by specifying the import path
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)







