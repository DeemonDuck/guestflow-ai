from tools.ticket_tool import create_ticket_tool
from llm_service import generate_guest_response
from rag.rag_service import retrieve_faq

VIP_GUESTS = ["Rahul", "Priya"]
def handle_instay(event):

    print("Running In-Stay Agent")

    guest_name = event.guest_name

    
    # Simulated guest question
    guest_question = event.guest_question
    
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
    
    if not guest_question:
        guest_question = "General guest assistance request"

    is_vip = guest_name in VIP_GUESTS

    
    # Retrieve FAQ context
    faq_result = retrieve_faq(guest_question)
    if escalation_required:
        faq_result = "Escalating issue to hotel manager."

    elif is_vip:
        faq_result += " Priority handling enabled for VIP guest."

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
        "ticket": ticket_result,
        "is_vip": is_vip,
        "escalation_required": escalation_required,
    }