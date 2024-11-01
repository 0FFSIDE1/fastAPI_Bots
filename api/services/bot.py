from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import json
from dotenv import load_dotenv


load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")
# Initialize the application variable as None
application = None

async def get_application():
    global application
    if not application:
        application = Application.builder().token(bot_token).build()
        application.add_handler(CommandHandler("start", start))
        # application.add_handler(CommandHandler("deposit", deposit))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await application.initialize()  # Asynchronously initialize the application
    return application

async def start(update: Update, context) -> None:
    await update.message.reply_text("Hello! How can I help you today?")


async def handle_message(update: Update, context) -> None:
    text = update.message.text.lower()
    user_name = update.message.chat.first_name
    print(f"{user_name} says: {text}")
    wallets = ['bitcoin', 'btc', 'eth', 'ethereum', 'usdt', 'tether','trc20','sol', 'solana', 'xrp', 'ripple', ]
    if "help" in text:
        await update.message.reply_text(f"How can I assist you {user_name}? Please provide details.")
    
    elif "hello" in text:
        await update.message.reply_text(f"Hello {user_name}, How are you doing?.")
    
    elif "deposit" in text:
        await update.message.reply_text("Select wallet address:\nBitcoin (BTC)\nUSDT (TRC20)\nSolana (SOL)\nRipple (XRP)\nEthereum (ETH)")
    
    elif "wallet" in text:
        await update.message.reply_text("How much do you want to deposit.")

    else:
        await context.bot.send_message(chat_id=chat_id, text=f"User Message: {text}")
        await update.message.reply_text("Thank you for your message!")


