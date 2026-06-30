def create_ticket_tool(
    guest_name: str,
    issue: str,
    room_number: str = "N/A",
    category: str = "General",
    priority: str = "Normal",
    time: str = "N/A"
) -> dict:

    print(f"\n SUPPORT TICKET CREATED")
    print(f"Guest    : {guest_name}")
    print(f"Room     : {room_number}")
    print(f"Category : {category}")
    print(f"Priority : {priority}")
    print(f"Time     : {time}")
    print(f"Issue    : {issue}")

    return {
        "status": "ticket_created",
        "guest": guest_name,
        "room": room_number,
        "category": category,
        "priority": priority,
        "issue": issue
    }
