def create_ticket_tool(guest_name, issue):

    print("\n SUPPORT TICKET CREATED")
    print(f"Guest: {guest_name}")
    print(f"Issue: {issue}")

    return {
        "status": "ticket_created",
        "issue": issue
    }