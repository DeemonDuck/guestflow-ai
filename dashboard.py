import streamlit as st
import requests


# Page Config
st.set_page_config(
    page_title="GuestFlow AI",
    layout="wide"
)

# Title
st.title("🏨 GuestFlow AI Dashboard")
st.subheader("Hotel Workflow Automation System")


# Sidebar Input Section
st.sidebar.header("Guest Event Input")


# Guest Name
guest_name = st.sidebar.text_input(
    "Guest Name"
)

# Event Type
event_type = st.sidebar.selectbox(
    "Event Type",
    [
        "booking_confirmed",
        "guest_request",
        "checkout_complete"
    ]
)

# Guest Question
guest_question = st.sidebar.text_area(
    "Guest Question"
)


# Trigger Workflow Button
if st.sidebar.button("Trigger Workflow"):

    payload = {
        "event_type": event_type,
        "guest_name": guest_name,
        "guest_question": guest_question
    }

    try:

        response = requests.post(
            "http://127.0.0.1:8000/webhook",
            json=payload
        )

        result = response.json()

        st.success("Workflow Executed Successfully")

        # Full JSON Response
        st.subheader("Full API Response")
        st.json(result)

        # Extract workflow result
        if "result" in result:

            workflow_result = result["result"]

            st.divider()

            st.subheader("Workflow Analysis")

            # Metrics
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "VIP Guest",
                    workflow_result.get("is_vip", False)
                )

            with col2:
                st.metric(
                    "Escalation Required",
                    workflow_result.get(
                        "escalation_required",
                        False
                    )
                )

            # AI Response
            st.subheader("AI Response")

            st.write(
                workflow_result.get(
                    "ai_response",
                    "No AI response available"
                )
            )

            # FAQ Result
            st.subheader("Retrieved FAQ")

            st.info(
                workflow_result.get(
                    "faq_result",
                    "No FAQ retrieved"
                )
            )

    except Exception as e:

        st.error(f"Error: {e}")