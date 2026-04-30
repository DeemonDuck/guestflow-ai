from tools.email_tool import send_email_tool


def handle_poststay(event):

    print("Running Post-Stay Agent")

    guest_name = event.guest_name

    email_result = send_email_tool(
        guest_name,
        "Thank you for staying with us! Please share feedback."
    )

    return {
        "agent": "PostStayAgent",
        "email": email_result
    }