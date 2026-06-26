from fastapi import FastAPI
from pydantic import BaseModel
from agents.orchestrator import route_event
from intent_classifier import classify_intent
from typing import Optional

app = FastAPI()


class WebhookEvent(BaseModel):
    event_type: Optional[str] = None
    guest_name: str
    guest_question: Optional[str] = None


@app.post("/webhook")
async def receive_webhook(event: WebhookEvent):

    # Auto-detect intent if event_type not provided
    if not event.event_type:
        text = event.guest_question or event.guest_name
        event.event_type = classify_intent(text)
        print(f"Auto-detected intent: {event.event_type}")

    result = route_event(event)

    return {
        "status": "success",
        "detected_intent": event.event_type,
        "result": result
    }
