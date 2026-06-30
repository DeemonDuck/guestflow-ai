"""Centralized configuration, read from environment variables.

Keeping these in one place (instead of scattered constants) is the first step
toward per-hotel configuration: a deployment only has to set env vars.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# Display name used in guest-facing messaging
HOTEL_NAME = os.getenv("HOTEL_NAME", "Our Hotel")

# Where manager/escalation alerts are sent. Falls back to the generic mailbox
# (GMAIL_RECIPIENT) so existing setups keep working without new config.
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL") or os.getenv("GMAIL_RECIPIENT")

# Default age (minutes) after which an open ticket is considered stale
ESCALATION_MINUTES = int(os.getenv("ESCALATION_MINUTES", "30"))

# Optional API key. When set, all API requests must send it in the
# 'X-API-Key' header. When unset, auth is DISABLED (development mode) — fine
# locally, but a deployment exposed to a network MUST set this.
API_KEY = os.getenv("API_KEY")

# Public review link (e.g. Google review URL). This is offered to EVERY guest
# regardless of how they rate their stay — never conditioned on a positive
# rating (conditioning it would be "review gating" and is not allowed).
REVIEW_LINK = os.getenv("REVIEW_LINK", "")

# Ratings (1-5) at or below this threshold trigger a private manager alert for
# service recovery. This does NOT affect the guest's public review invitation.
REVIEW_ALERT_THRESHOLD = int(os.getenv("REVIEW_ALERT_THRESHOLD", "3"))

# Local LLM (Ollama) settings — swappable without code changes.
LLM_MODEL = os.getenv("LLM_MODEL", "phi3")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.5"))

# Shown to the guest when the LLM is unavailable, so a model outage never
# breaks the workflow (the ticket/email still go through).
LLM_FALLBACK_MESSAGE = os.getenv(
    "LLM_FALLBACK_MESSAGE",
    "Thanks for reaching out — a member of our team will follow up with you shortly.",
)
