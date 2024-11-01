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
keep_alive_task_running = False  # Flag to check if keep-alive is running

# Initialize the Telegram bot application
async def init_application():
    global application
    if application is None:
        application = Application.builder().token(bot_token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await application.initialize()

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
    elif any(wallet in text for wallet in wallets):
        await update.message.reply_text("Enter the amount you'd like to deposit?")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"User Message: {text}")
        await update.message.reply_text("Thank you for your message!")

# Background task to keep the bot active
async def keep_bot_active():
    global keep_alive_task_running
    keep_alive_task_running = True
    while keep_alive_task_running:
        try:
            response = await http_client.post(webhook_url, json={"message": "Keep bot active"})  # Sending a message to the bot
            print("Sent a keep-alive message to the bot")
            await asyncio.sleep(180)  # Sleep for 3 minutes
        except Exception as e:
            print(f"Error sending keep-alive message: {e}")
            await asyncio.sleep(60)  # Wait before retrying

# POST method to trigger the keep-alive background task
@app.post("/keep-alive")
async def trigger_keep_alive(background_tasks: BackgroundTasks):
    """Starts the background task to send keep-alive messages every 3 minutes."""
    global keep_alive_task_running
    if not keep_alive_task_running:
        background_tasks.add_task(keep_bot_active)  # Start the background task
        return {"status": "Keep-alive messages will be sent every 3 minutes."}
    else:
        return {"status": "Keep-alive task is already running."}

# Webhook endpoint to receive updates from Telegram
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

# Startup event: Set the webhook with Telegram
@app.on_event("startup")
async def set_webhook():
    await init_application()  # Initialize the application once during startup
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
    global keep_alive_task_running
    keep_alive_task_running = False  # Stop the keep-alive task
    await http_client.aclose()
    print("HTTP client closed.")

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return JSONResponse(content={"message": "An internal error occurred."}, status_code=500)