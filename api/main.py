from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.post("/notify")
def notify(data: str):
    try:
        message = f"🚀 New Event: {data}"
        requests.post(os.getenv("DISCORD_WEBHOOK"), json={
            "content": message
        })

        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/taiga/webhook")
async def taiga_webhook(request: Request):
    try:
        payload = await request.json()

        event_type = payload.get("type")
        action = payload.get("action")
        data = payload.get("data", {})

        message = f"📢 {event_type.upper()} {action.upper()}\n"

        if event_type == "task":
            message += f"📝 {data.get('subject')}"

        requests.post(os.getenv("DISCORD_WEBHOOK"), json={"content": message})

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def health_check():
    return {"status": "healthy"}
