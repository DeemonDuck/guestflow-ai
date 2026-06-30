from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel
from agents.orchestrator import route_event
from intent_classifier import classify_intent
from tools.ticket_tool import (
    list_tickets,
    update_ticket_status,
    find_stale_tickets,
    escalate_stale_tickets,
)
from tools.profile_tool import get_profile, save_profile
from tools.feedback_tool import submit_feedback, list_feedback
from tools.analytics_tool import get_analytics
from tools.insights_tool import get_insights
from tools.digest_tool import send_digest, compose_digest
from config import ESCALATION_MINUTES, API_KEY
from typing import Optional


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Require a valid X-API-Key header — but only when an API key is configured.

    If API_KEY is unset, authentication is disabled (development mode).
    """
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


if not API_KEY:
    print(
        "WARNING: API_KEY is not set — the API is UNAUTHENTICATED. "
        "Set API_KEY in the environment before exposing this service on a network."
    )

# Apply the key check to every endpoint (no-op when API_KEY is unset)
app = FastAPI(dependencies=[Depends(require_api_key)])


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


class ProfileUpdate(BaseModel):
    contact_email: Optional[str] = None
    preferences: Optional[str] = None
    is_vip: Optional[bool] = None
    notes: Optional[str] = None


class FeedbackSubmit(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None


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


@app.get("/tickets/escalations")
async def get_escalations(minutes: int = ESCALATION_MINUTES):
    """List open tickets unattended for longer than `minutes` (read-only)."""
    return {"minutes": minutes, "stale_tickets": find_stale_tickets(minutes)}


@app.post("/tickets/escalations/run")
async def run_escalations(minutes: int = ESCALATION_MINUTES):
    """Alert a manager about stale open tickets (each ticket escalated once)."""
    return {"minutes": minutes, "escalated": escalate_stale_tickets(minutes)}


@app.get("/profiles/{guest_name}")
async def read_profile(guest_name: str):
    """Return a guest's stored profile (or null if none exists)."""
    return {"profile": get_profile(guest_name)}


@app.post("/profiles/{guest_name}")
async def write_profile(guest_name: str, update: ProfileUpdate):
    """Create or update a guest profile (merge upsert: omitted fields are kept)."""
    profile = save_profile(
        guest_name,
        contact_email=update.contact_email,
        preferences=update.preferences,
        is_vip=update.is_vip,
        notes=update.notes,
    )
    return {"profile": profile}


@app.get("/feedback")
async def get_feedback():
    """List all submitted guest feedback."""
    return {"feedback": list_feedback()}


@app.post("/feedback/{guest_name}")
async def post_feedback(guest_name: str, feedback: FeedbackSubmit):
    """Record a guest's post-stay feedback (alerts manager if negative)."""
    return submit_feedback(guest_name, rating=feedback.rating, comment=feedback.comment)


@app.get("/analytics")
async def analytics():
    """Owner-facing ROI metrics aggregated from tickets and feedback."""
    return get_analytics()


@app.get("/insights")
async def insights():
    """Proactive operations insights (systemic issues, repeat rooms, feedback themes)."""
    return {"insights": get_insights()}


@app.get("/digest")
async def digest_preview():
    """Preview the manager digest body without sending it."""
    return {"digest": compose_digest()}


@app.post("/digest/run")
async def digest_run():
    """Compose and email the operations digest to the manager."""
    return send_digest()
