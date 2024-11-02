import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")

# Create an Application instance but don't initialize yet
application = Application.builder().token(bot_token).build()
application_initialized = False

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hello! How can I help you today?")

async def handle_message(update: Update, context) -> None:
    """Handle incoming text messages."""
    text = update.message.text
    if "help" in text.lower():
        await update.message.reply_text("How can I assist you? Please provide details.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"User Message: {text}")
        await update.message.reply_text("Thank you for your message! A support representative will reach out if needed.")

async def get_application():
    global application_initialized
    if not application_initialized:
        # Initialize the Application asynchronously
        await application.initialize()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application_initialized = True
    return application

async def process_update(application, update: Update):
    """Process the incoming update."""
    await application.process_update(update)
