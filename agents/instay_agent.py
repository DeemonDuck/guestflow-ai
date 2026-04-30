from tools.ticket_tool import create_ticket_tool


def handle_instay(event):

    print("Running In-Stay Agent")

    guest_name = event.guest_name

    ticket_result = create_ticket_tool(
        guest_name,
        "Guest requested room service"
    )

    return {
        "agent": "InStayAgent",
        "ticket": ticket_result
    }