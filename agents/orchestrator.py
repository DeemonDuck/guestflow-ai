from agents.prestay_agent import handle_prestay
from agents.instay_agent import handle_instay
from agents.poststay_agent import handle_poststay


def route_event(event):

    event_type = event.event_type

    print(f"Routing Event: {event_type}")

    if event_type == "booking_confirmed":
        return handle_prestay(event)

    elif event_type == "guest_request":
        return handle_instay(event)

    elif event_type == "checkout_complete":
        return handle_poststay(event)

    else:
        return {
            "error": "Unknown event type"
        }