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
