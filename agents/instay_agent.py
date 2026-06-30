from tools.ticket_tool import create_ticket_tool
from tools.crm_tool import get_guest_history_tool
from tools.profile_tool import get_profile
from llm_service import generate_guest_response
from rag.rag_service import retrieve_faq


def handle_instay(event):

    print("Running In-Stay Agent")

    guest_name = event.guest_name

    # Guest question from webhook
    guest_question = event.guest_question

    # Fallback if question missing
    if not guest_question:
        guest_question = "General guest assistance request"

    # Load stored guest profile once (drives VIP status + personalisation)
    profile = get_profile(guest_name)

    # Escalation detection
    escalation_required = False

    urgent_keywords = [
        "angry",
        "refund",
        "complaint",
        "bad service",
        "cancel",
        "emergency"
    ]

    if any(word in guest_question.lower() for word in urgent_keywords):
        escalation_required = True

    # VIP detection — driven by the guest's stored profile
    is_vip = bool(profile and profile.get("is_vip"))

    # Retrieve FAQ context
    faq_result = retrieve_faq(guest_question)

    # Workflow logic
    if escalation_required:
        faq_result = "Escalating issue to hotel manager."

    elif is_vip:
        faq_result += " Priority handling enabled for VIP guest."

    print(f"\nFAQ MATCH: {faq_result}")

    # Stored preferences (if any) to personalise the reply
    preferences = profile["preferences"] if profile and profile.get("preferences") else "None on file"

    # AI-generated response
    ai_response = generate_guest_response(
        f"""
        You are a hotel guest support assistant.

        Respond in:
        - 2 to 3 short sentences
        - conversational tone
        - concise style
        - no email formatting
        - no greetings/signatures

        Guest Question:
        {guest_question}

        Relevant Hotel Information:
        {faq_result}

        Known Guest Preferences:
        {preferences}
        """
    )

    # Create support ticket
    ticket_result = create_ticket_tool(
        guest_name=guest_name,
        issue=guest_question,
        room_number=getattr(event, "room_number", "N/A"),
        category=getattr(event, "category", "General"),
        priority="High" if escalation_required else getattr(event, "priority", "Normal"),
        time=getattr(event, "time", "N/A")
    )

    # Prior CRM events for this guest (context for staff)
    history = get_guest_history_tool(guest_name)

    # Return workflow result
    return {
        "agent": "InStayAgent",
        "faq_result": faq_result,
        "ai_response": ai_response,
        "ticket": ticket_result,
        "is_vip": is_vip,
        "escalation_required": escalation_required,
        "history": history,
        "preferences": preferences
    }