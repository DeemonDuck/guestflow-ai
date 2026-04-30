from tools.email_tool import send_email_tool
from tools.crm_tool import update_crm_tool


def handle_prestay(event):

    print("Running Pre-Stay Agent")

    guest_name = event.guest_name

    email_result = send_email_tool(
        guest_name,
        "Your booking has been confirmed!"
    )

    crm_result = update_crm_tool(
        guest_name,
        event.event_type
    )

    return {
        "agent": "PreStayAgent",
        "email": email_result,
        "crm": crm_result
    }