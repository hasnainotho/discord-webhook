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
        by_user = payload.get("by", {})

        # Build Discord message
        username = by_user.get("full_name", "Unknown")
        subject = data.get("subject", "N/A")
        ref = data.get("ref", "")
        project = data.get("project", {}).get("name", "Unknown")

        # Handle different event types
        if event_type == "task":
            emoji = "✅"
            message = f"{emoji} **Task {action.upper()}** in {project}\n📝 {subject}"
        elif event_type == "userstory":
            emoji = "📖"
            message = f"{emoji} **User Story {action.upper()}** in {project}\n📖 #{ref} - {subject}"
        elif event_type == "issue":
            emoji = "🐛"
            message = f"{emoji} **Issue {action.upper()}** in {project}\n🐛 {subject}"
        else:
            emoji = "🔔"
            message = f"{emoji} **{event_type.upper()} {action.upper()}** in {project}\n{subject}"

        message += f"\n👤 By: {username}"

        response = requests.post(os.getenv("DISCORD_WEBHOOK"), json={"content": message})
        response.raise_for_status()

        return {"status": "ok", "type": event_type, "action": action}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def health_check():
    return {"status": "healthy"}
