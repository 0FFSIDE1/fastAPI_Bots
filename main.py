import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI 
import requests
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import os
from dotenv import load_dotenv
from api.v1.routes.bot import chinedu
from fastapi.responses import JSONResponse
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from api.services.bot import handle_message, start
load_dotenv()


# Initialize the application variable as None
application = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global application
    """Sets the webhook for the Telegram bot if not already set."""
    if os.getenv("WEBHOOK_INITIALIZED") != "true":
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        response = requests.post(url, json={"url": webhook_url})
        if response.status_code == 200:
            print("Webhook set successfully!")
            os.environ["WEBHOOK_INITIALIZED"] = "true"
        else:
            print(f"Failed to set webhook: {response.json()}")

    
    if not application:
        # Create an Application instance and add handlers
        application = Application.builder().token(bot_token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await application.initialize()  # Initialize the application
        print("application initailized")
    yield
    

app = FastAPI(lifespan=lifespan)
app.router.lifespan_context = lifespan

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chinedu)


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return JSONResponse(content={"message": "An internal error occurred."}, status_code=500)

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to ChineduIsABot",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)