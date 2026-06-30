import hmac

from fastapi import FastAPI, Depends, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import ESCALATION_MINUTES, API_KEY, REQUIRE_AUTH

# Fail-closed: in production (REQUIRE_AUTH) refuse to start without a key, so a
# missing env var can never silently expose the API. Checked BEFORE loading the
# heavy agent/LLM modules so it fails fast.
if REQUIRE_AUTH and not API_KEY:
    raise RuntimeError(
        "REQUIRE_AUTH is set but API_KEY is missing. Set API_KEY before starting."
    )

from agents.orchestrator import route_event
from intent_classifier import classify_intent
from tools.ticket_tool import (
    list_tickets,
    update_ticket_status,
    find_stale_tickets,
    escalate_stale_tickets,
)
from tools.profile_tool import get_profile, save_profile, erase_guest_data
from tools.feedback_tool import submit_feedback, list_feedback
from tools.analytics_tool import get_analytics
from tools.insights_tool import get_insights
from tools.digest_tool import send_digest, compose_digest


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Require a valid X-API-Key header — but only when an API key is configured.

    If API_KEY is unset, authentication is disabled (development mode).
    """
    if API_KEY:
        # Constant-time comparison to avoid timing-based key recovery
        if not x_api_key or not hmac.compare_digest(x_api_key, API_KEY):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


if not API_KEY:
    print(
        "WARNING: API_KEY is not set — the API is UNAUTHENTICATED. "
        "Set API_KEY in the environment before exposing this service on a network."
    )

# Disable interactive docs / schema when a key is configured (production), so the
# full API surface isn't publicly discoverable. They stay on for local dev.
_docs_enabled = API_KEY is None

# Rate limiter (per client IP) to curb abuse / DoS / email spam / LLM cost
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    dependencies=[Depends(require_api_key)],
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class WebhookEvent(BaseModel):
    event_type: Optional[str] = Field(default=None, max_length=50)
    guest_name: str = Field(min_length=1, max_length=120)
    room_number: Optional[str] = Field(default="N/A", max_length=20)
    category: Optional[str] = Field(default="General", max_length=50)
    priority: Optional[str] = Field(default="Normal", max_length=20)
    time: Optional[str] = Field(default="N/A", max_length=50)
    guest_question: Optional[str] = Field(default=None, max_length=2000)


class TicketStatusUpdate(BaseModel):
    status: str = Field(max_length=20)


class ProfileUpdate(BaseModel):
    contact_email: Optional[EmailStr] = None
    preferences: Optional[str] = Field(default=None, max_length=1000)
    is_vip: Optional[bool] = None
    notes: Optional[str] = Field(default=None, max_length=1000)


class FeedbackSubmit(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)


@app.post("/webhook")
@limiter.limit("60/minute")
async def receive_webhook(request: Request, event: WebhookEvent):

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
@limiter.limit("12/minute")
async def run_escalations(request: Request, minutes: int = ESCALATION_MINUTES):
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


@app.delete("/profiles/{guest_name}")
async def delete_profile(guest_name: str):
    """Erase a guest's personal data (profile + feedback removed, tickets anonymized)."""
    return erase_guest_data(guest_name)


@app.get("/feedback")
async def get_feedback():
    """List all submitted guest feedback."""
    return {"feedback": list_feedback()}


@app.post("/feedback/{guest_name}")
@limiter.limit("30/minute")
async def post_feedback(request: Request, guest_name: str, feedback: FeedbackSubmit):
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
@limiter.limit("6/minute")
async def digest_run(request: Request):
    """Compose and email the operations digest to the manager."""
    return send_digest()
