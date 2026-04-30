def send_email_tool(guest_name, message):

    print("\n EMAIL TOOL ACTIVATED")
    print(f"Sending email to: {guest_name}")
    print(f"Message: {message}")

    return {
        "status": "email_sent",
        "guest": guest_name
    }