# api/main.py

from fastapi import FastAPI, Request, HTTPException
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import json
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")

app = FastAPI()

# Initialize the application variable as None
application = None

async def get_application():
    global application
    if not application:
        application = Application.builder().token(bot_token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await application.initialize()  # Asynchronously initialize the application
    return application

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hello! How can I help you today?")

async def handle_message(update: Update, context) -> None:
    text = update.message.text
    if "help" in text.lower():
        await update.message.reply_text("How can I assist you? Please provide details.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"User Message: {text}")
        await update.message.reply_text("Thank you for your message!")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    application = await get_application()
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}


@app.on_event("startup")
async def set_webhook():
    """Sets the webhook for the Telegram bot if not already set."""
    if os.getenv("WEBHOOK_INITIALIZED") != "true":
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        response = requests.post(url, json={"url": webhook_url})
        if response.status_code == 200:
            print("Webhook set successfully!")
            os.environ["WEBHOOK_INITIALIZED"] = "true"
        else:
            print(f"Failed to set webhook: {response.json()}")

