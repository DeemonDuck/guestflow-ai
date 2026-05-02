from tools.ticket_tool import create_ticket_tool
from llm_service import generate_guest_response


def handle_instay(event):

    print("Running In-Stay Agent")

    guest_name = event.guest_name

    # Simulated guest issue
    guest_issue = "Guest requested extra towels"

    # Generate AI response
    ai_response = generate_guest_response(
        f"""
        You are a professional hotel assistant.

        Respond politely to this guest request:
        {guest_issue}
        """
    )

    # Create support ticket
    ticket_result = create_ticket_tool(
        guest_name,
        guest_issue
    )

    return {
        "agent": "InStayAgent",
        "ai_response": ai_response,
        "ticket": ticket_result
    }