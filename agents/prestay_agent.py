from tools.email_tool import send_email_tool
from tools.crm_tool import (
    update_crm_tool,
    get_guest_history_tool
)

from memory import store_memory, retrieve_memory


def handle_prestay(event):

    print("Running Pre-Stay Agent")

    guest_name = event.guest_name

    # CRM History
    history = get_guest_history_tool(guest_name)
    print(f"Previous History: {history}")

    # Qdrant Semantic Memory
    memory_results = retrieve_memory(event.event_type)
    print(f"Semantic Memory: {memory_results}")

    email_result = send_email_tool(
        guest_name,
        "Your booking has been confirmed!"
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
        "memory": str(memory_results)
    }