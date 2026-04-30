crm_database = []


def update_crm_tool(guest_name, event_type):

    entry = {
        "guest_name": guest_name,
        "event_type": event_type
    }

    crm_database.append(entry)

    print("\n CRM UPDATED")
    print(entry)

    return {
        "status": "crm_updated",
        "data": entry
    }