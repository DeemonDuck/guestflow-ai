from fastapi import FastAPI
from pydantic import BaseModel
from agents.orchestrator import route_event

# Create FastAPI app
app = FastAPI()


# Define structure of incoming webhook data
class WebhookEvent(BaseModel):
    event_type: str
    guest_name: str


# Create webhook endpoint
@app.post("/webhook")
async def receive_webhook(event: WebhookEvent):

    print("Webhook received!")

    result = route_event(event)

    return {
    "status": "success",
    "result": result
    }