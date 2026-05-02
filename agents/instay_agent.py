from tools.ticket_tool import create_ticket_tool
from llm_service import generate_guest_response
from rag.rag_service import retrieve_faq


def handle_instay(event):

    print("Running In-Stay Agent")

    guest_name = event.guest_name

    # Simulated guest question
    guest_question = event.guest_question
    if not guest_question:
        guest_question = "General guest assistance request"

    # Retrieve FAQ context
    faq_result = retrieve_faq(guest_question)

    print(f"\nFAQ MATCH: {faq_result}")

    # Mock AI response
    ai_response = generate_guest_response(
        f"""
        Guest Question:
        {guest_question}

        Relevant Hotel Information:
        {faq_result}
        """
    )

    # Create support ticket
    ticket_result = create_ticket_tool(
        guest_name,
        guest_question
    )

    return {
        "agent": "InStayAgent",
        "faq_result": faq_result,
        "ai_response": ai_response,
        "ticket": ticket_result
    }