from fastapi import FastAPI, Request, BackgroundTasks
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# Environment variables
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")

app = FastAPI()
application: Application = None
http_client = httpx.AsyncClient()  # Global HTTP client for reusability
initialized = False  # Flag to track initialization

# Initialize the Telegram bot application
async def init_application():
    global application, initialized
    if application is None and not initialized:
        application = Application.builder().token(bot_token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await application.initialize()
        initialized = True  # Mark as initialized

# Handlers for bot commands and messages
async def start(update: Update, context) -> None:
    await update.message.reply_text("Hello! How can I help you today?")

async def handle_message(update: Update, context) -> None:
    text = update.message.text.lower()
    wallets = ['bitcoin', 'btc', 'usdt', 'trc20', 'solana', 'sol', 'ripple', 'xrp', 'eth', 'ethereum']

    if "help" in text:
        await update.message.reply_text("How can I assist you? Please provide details.")
    elif "deposit" in text:
        await update.message.reply_text("Select wallet address:\nBitcoin (BTC)\nUSDT (TRC20)\nSolana (SOL)\nRipple (XRP)\nEthereum (ETH)")
        if text in wallets:
            await update.message.reply_text("Enter amount you'd like to deposit?")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"User Message: {text}")
        await update.message.reply_text("Thank you for your message!")

# Background task to keep the bot active
async def keep_bot_active():
    while True:
        try:
            # Send a keep-alive message to the admin chat
            await http_client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": "Bot is active!"}
            )
            print("Sent a keep-alive message to the admin chat.")
        except Exception as e:
            print(f"Error sending keep-alive message: {e}")
        await asyncio.sleep(180)  # Sleep for 3 minutes

# POST method to trigger the keep-alive background task
@app.post("/keep-alive")
async def trigger_keep_alive(background_tasks: BackgroundTasks):
    """Starts the background task to send keep-alive messages every 3 minutes."""
    background_tasks.add_task(keep_bot_active)  # Start the background task
    return {"status": "Keep-alive messages will be sent every 3 minutes."}

# Webhook endpoint to receive updates from Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):
    await init_application()  # Ensure that application is initialized
    data = await request.json()
    update = Update.de_json(data, application.bot)  # Safely access application.bot
    await application.process_update(update)
    return {"status": "ok"}

# Startup event: Set the webhook with Telegram
@app.on_event("startup")
async def set_webhook():
    if os.getenv("WEBHOOK_INITIALIZED") != "true":
        try:
            response = await http_client.post(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                json={"url": webhook_url}
            )
            if response.status_code == 200:
                print("Webhook set successfully!")
                os.environ["WEBHOOK_INITIALIZED"] = "true"
            else:
                print(f"Failed to set webhook: {response.json()}")
        except Exception as e:
            print(f"Error setting webhook: {e}")

# Shutdown event: Cleanup resources
@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    print("HTTP client closed.")

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return JSONResponse(content={"message": "An internal error occurred."}, status_code=500)