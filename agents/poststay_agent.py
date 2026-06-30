from tools.feedback_tool import request_feedback


def handle_poststay(event):

    print("Running Post-Stay Agent")

    guest_name = event.guest_name

    # Ask the guest for feedback. The public review invite (if configured) is
    # included for every guest, never conditioned on sentiment.
    email_result = request_feedback(guest_name)

    return {
        "agent": "PostStayAgent",
        "email": email_result
    }
