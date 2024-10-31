from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import json
from asgiref.sync import async_to_sync

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")

app = FastAPI()

# Create an Application instance but don't initialize yet
application = Application.builder().token(bot_token).build()
application_initialized = False

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hello! How can I help you today?")

async def handle_message(update: Update, context) -> None:
    text = update.message.text
    if "help" in text.lower():
        await update.message.reply_text("How can I assist you? Please provide details.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"User Message: {text}")
        await update.message.reply_text(
            "Thank you for your message! A support representative will reach out if needed."
        )

@app.on_event("startup")
async def startup_event():
    global application_initialized
    if not application_initialized:
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await application.initialize()
        application_initialized = True

@app.post("/webhook")
async def telegram_webhook(request: Request):
    if not application_initialized:
        raise HTTPException(status_code=503, detail="Bot not initialized")

    # Parse the request body as JSON
    data = await request.json()
    update = Update.de_json(data, application.bot)

    # Process the update
    await application.process_update(update)

    return {"status": "ok"}
