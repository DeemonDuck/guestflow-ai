from fastapi import FastAPI
from pydantic import BaseModel
from agents.orchestrator import route_event
from intent_classifier import classify_intent
from tools.ticket_tool import list_tickets, update_ticket_status
from typing import Optional

app = FastAPI()


class WebhookEvent(BaseModel):
    event_type: Optional[str] = None
    guest_name: str
    room_number: Optional[str] = "N/A"
    category: Optional[str] = "General"
    priority: Optional[str] = "Normal"
    time: Optional[str] = "N/A"
    guest_question: Optional[str] = None


class TicketStatusUpdate(BaseModel):
    status: str


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


@app.get("/tickets")
async def get_tickets(status: Optional[str] = None):
    """List tickets, optionally filtered by status (open/in_progress/resolved)."""
    return {"tickets": list_tickets(status)}


@app.patch("/tickets/{ticket_id}")
async def patch_ticket(ticket_id: int, update: TicketStatusUpdate):
    """Move a ticket to a new lifecycle state."""
    return update_ticket_status(ticket_id, update.status)
