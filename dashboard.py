import streamlit as st
import requests
import base64


API_BASE = "http://127.0.0.1:8000"


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


st.sidebar.caption("💡 Leave blank to auto-detect intent from your message")
event_type = st.sidebar.text_input("Event Type (optional)")


guest_question = st.sidebar.text_area(
    "Guest Question"
)


# -----------------------------
# TABS: Workflow + Tickets
# -----------------------------
tab_workflow, tab_tickets = st.tabs(["⚙️ Workflow", "🎫 Tickets"])


# =============================
# WORKFLOW TAB
# =============================
with tab_workflow:

    if st.sidebar.button("Trigger Workflow"):

        payload = {
            "event_type": event_type,
            "guest_name": guest_name,
            "guest_question": guest_question
        }

        try:

            response = requests.post(
                f"{API_BASE}/webhook",
                json=payload
            )

            result = response.json()

            st.success("Workflow Executed Successfully")

            # Show detected intent
            detected = result.get("detected_intent")
            if detected:
                st.info(f"🧠 Detected Intent: `{detected}`")

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


# =============================
# TICKETS TAB
# =============================
with tab_tickets:

    st.subheader("Support Tickets")

    status_filter = st.selectbox(
        "Filter by status",
        ["all", "open", "in_progress", "resolved"]
    )

    try:
        params = {} if status_filter == "all" else {"status": status_filter}
        resp = requests.get(f"{API_BASE}/tickets", params=params)
        tickets = resp.json().get("tickets", [])

        if not tickets:
            st.info("No tickets found for this filter.")

        else:
            st.caption(f"{len(tickets)} ticket(s)")

            for t in tickets:
                tid = t["ticket_id"]
                with st.expander(
                    f"#{tid} · {t['category']} · {t['priority']} · [{t['ticket_status']}]"
                ):
                    st.write(f"**Guest:** {t['guest_name']}")
                    st.write(f"**Room:** {t['room_number']}")
                    st.write(f"**Issue:** {t['issue']}")
                    st.write(f"**Created:** {t['created_at']}")
                    st.write(f"**Updated:** {t['updated_at']}")

                    options = ["open", "in_progress", "resolved"]
                    current = t["ticket_status"]
                    new_status = st.selectbox(
                        "Change status",
                        options,
                        index=options.index(current) if current in options else 0,
                        key=f"status_{tid}"
                    )

                    if st.button("Update", key=f"update_{tid}"):
                        patch = requests.patch(
                            f"{API_BASE}/tickets/{tid}",
                            json={"status": new_status}
                        )
                        out = patch.json()
                        if out.get("status") == "ticket_updated":
                            st.success(f"Ticket #{tid} → {new_status}")
                            st.rerun()
                        else:
                            st.error(out.get("message", "Update failed"))

    except Exception as e:
        st.error(f"Could not load tickets: {e}")