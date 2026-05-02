import streamlit as st
import requests
import base64


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GuestFlow AI",
    layout="wide"
)


# -----------------------------
# LOAD BACKGROUND IMAGE
# -----------------------------
def get_base64_image(image_path):

    with open(image_path, "rb") as img_file:
        return base64.b64encode(
            img_file.read()
        ).decode()


bg_image = get_base64_image(
    "assets/resort_bg.png"
)


# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown(
    f"""
    <style>

    .stApp {{
        background-image: url("data:image/png;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .main {{
        background-color: rgba(0, 0, 0, 0.45);
        border-radius: 15px;
        padding: 20px;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.65);
    }}

    div[data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.08);
        padding: 15px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }}

    div[data-testid="stVerticalBlock"] {{
        background-color: rgba(0, 0, 0, 0.35);
        border-radius: 15px;
        padding: 15px;
    }}

    h1, h2, h3, p, label, div {{
        color: white !important;
    }}

    .stTextInput input {{
        color: white !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
    }}

    .stTextArea textarea {{
        color: white !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# TITLE
# -----------------------------
st.title("🏨 GuestFlow AI Dashboard")
st.subheader("Hotel Workflow Automation System")


# -----------------------------
# SIDEBAR INPUTS
# -----------------------------
st.sidebar.header("Guest Event Input")


guest_name = st.sidebar.text_input(
    "Guest Name"
)


event_type = st.sidebar.selectbox(
    "Event Type",
    [
        "booking_confirmed",
        "guest_request",
        "checkout_complete"
    ]
)


guest_question = st.sidebar.text_area(
    "Guest Question"
)


# -----------------------------
# WORKFLOW BUTTON
# -----------------------------
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

        # Full API Response
        st.subheader("Full API Response")
        st.json(result)

        # Extract Workflow Result
        workflow_result = result.get("result")

        if workflow_result:

            st.divider()

            st.subheader("Workflow Analysis")

            # Metrics
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "VIP Guest",
                    workflow_result.get(
                        "is_vip",
                        False
                    )
                )

            with col2:
                st.metric(
                    "Escalation Required",
                    workflow_result.get(
                        "escalation_required",
                        False
                    )
                )

            # Agent Used
            st.subheader("Agent Used")

            st.success(
                workflow_result.get(
                    "agent",
                    "Unknown Agent"
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

            # Guest History
            st.subheader("Guest History")

            st.write(
                workflow_result.get(
                    "history",
                    []
                )
            )

    except Exception as e:

        st.error(f"Error: {e}")