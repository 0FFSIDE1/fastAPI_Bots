import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import os
import httpx  # Using httpx for async requests
from dotenv import load_dotenv
from api.v1.routes.bot import chinedu

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")

app = FastAPI()

@app.on_event("startup")
async def set_webhook():
    """Sets the webhook for the Telegram bot if not already set."""
    if os.getenv("WEBHOOK_INITIALIZED") != "true":
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"url": webhook_url})
        if response.status_code == 200:
            print("Webhook set successfully!")
            os.environ["WEBHOOK_INITIALIZED"] = "true"
        else:
            print(f"Failed to set webhook: {response.json()}")

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

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to ChineduIsABot",
        "URL": "",
    }

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
