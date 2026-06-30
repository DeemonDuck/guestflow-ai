from tools.email_tool import send_email_tool
from tools.crm_tool import (
    update_crm_tool,
    get_guest_history_tool
)

from memory import store_memory, retrieve_memory
from tools.profile_tool import get_profile
from llm_service import generate_guest_response

def handle_prestay(event):

    print("Running Pre-Stay Agent")

    guest_name = event.guest_name

    # CRM History
    history = get_guest_history_tool(guest_name)
    print(f"Previous History: {history}")

    # Qdrant Semantic Memory
    memory_results = retrieve_memory(
        f"{guest_name} booking preferences"
    )
    
    print(f"Semantic Memory: {memory_results}")

    memory_context = str(memory_results)

    # Load stored guest preferences (if any) to personalise the confirmation
    profile = get_profile(guest_name)
    preferences = profile["preferences"] if profile and profile.get("preferences") else "None on file"

    ai_response = generate_guest_response(
        f"""
        You are a luxury hotel booking assistant.

        Respond in:
        - 2 short conversational sentences
        - warm hospitality tone
        - concise style
        - no email formatting
        - no greetings/signatures

        Guest Name:
        {guest_name}

        Guest Event:
        {event.event_type}

        Known Guest Preferences:
        {preferences}

        Previous Guest Memory:
        {memory_context}

        CRM History:
        {history}

        Generate a personalized booking confirmation response.
        """
    )   

    email_result = send_email_tool(
        guest_name=guest_name,
        message=ai_response,
        category="Booking Confirmation",
        priority="Normal",
        recipient=(profile.get("contact_email") if profile else None)
    )

    crm_result = update_crm_tool(
        guest_name,
        event.event_type
    )

    # Store new semantic memory
    store_memory(
        guest_name,
        f"Guest triggered {event.event_type}"
    )

    return {
        "agent": "PreStayAgent",
        "email": email_result,
        "crm": crm_result,
        "memory": str(memory_results),
        "ai_response": ai_response,
        "preferences": preferences,
    }