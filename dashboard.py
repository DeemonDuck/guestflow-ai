import streamlit as st
import requests
import base64
import os

from dotenv import load_dotenv

load_dotenv()

API_BASE = "http://127.0.0.1:8000"

# Send the API key with every request when one is configured
_API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-Key": _API_KEY} if _API_KEY else {}


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
tab_workflow, tab_tickets, tab_profiles, tab_feedback, tab_analytics = st.tabs(
    ["⚙️ Workflow", "🎫 Tickets", "👤 Profiles", "⭐ Feedback", "📊 Analytics"]
)


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
                json=payload,
                headers=HEADERS
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

                # Ticket (created for in-stay guest requests)
                ticket = workflow_result.get("ticket")
                if ticket and ticket.get("ticket_id"):
                    st.subheader("Ticket Created")
                    st.write(
                        f"#{ticket['ticket_id']} · "
                        f"{ticket.get('category', 'General')} · "
                        f"{ticket.get('priority', 'Normal')} · "
                        f"[{ticket.get('ticket_status', 'open')}]"
                    )

                # FAQ Result (only for requests that retrieved one)
                faq_result = workflow_result.get("faq_result")
                if faq_result:
                    st.subheader("Retrieved FAQ")
                    st.info(faq_result)

                # Guest History (only when the guest has prior events)
                history = workflow_result.get("history")
                if history:
                    st.subheader("Guest History")
                    st.write(history)

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
        resp = requests.get(f"{API_BASE}/tickets", params=params, headers=HEADERS)
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
                            json={"status": new_status},
                            headers=HEADERS
                        )
                        out = patch.json()
                        if out.get("status") == "ticket_updated":
                            st.success(f"Ticket #{tid} → {new_status}")
                            st.rerun()
                        else:
                            st.error(out.get("message", "Update failed"))

    except Exception as e:
        st.error(f"Could not load tickets: {e}")


# =============================
# PROFILES TAB
# =============================
with tab_profiles:

    st.subheader("Guest Profiles & Preferences")

    lookup_name = st.text_input("Guest name", key="profile_lookup")

    if lookup_name:
        # Load existing profile (if any) to pre-fill the form
        existing = {}
        try:
            resp = requests.get(f"{API_BASE}/profiles/{lookup_name}", headers=HEADERS)
            existing = resp.json().get("profile") or {}
        except Exception as e:
            st.error(f"Could not load profile: {e}")

        if existing:
            st.caption(
                f"Existing profile · created {existing.get('created_at', '?')} · "
                f"updated {existing.get('updated_at', '?')}"
            )
        else:
            st.caption("No profile yet — saving will create one.")

        contact_email = st.text_input(
            "Contact email",
            value=existing.get("contact_email") or "",
            key="profile_email"
        )
        preferences = st.text_area(
            "Preferences",
            value=existing.get("preferences") or "",
            key="profile_prefs",
            placeholder="High floor, extra pillows, vegetarian breakfast"
        )
        is_vip = st.checkbox(
            "VIP guest",
            value=bool(existing.get("is_vip", False)),
            key="profile_vip"
        )
        notes = st.text_area(
            "Notes",
            value=existing.get("notes") or "",
            key="profile_notes"
        )

        if st.button("Save Profile", key="profile_save"):
            payload = {
                "contact_email": contact_email or None,
                "preferences": preferences or None,
                "is_vip": is_vip,
                "notes": notes or None,
            }
            try:
                save = requests.post(
                    f"{API_BASE}/profiles/{lookup_name}",
                    json=payload,
                    headers=HEADERS
                )
                saved = save.json().get("profile")
                if saved:
                    st.success(f"Profile saved for {lookup_name}")
                    st.json(saved)
                else:
                    st.error("Save failed")
            except Exception as e:
                st.error(f"Could not save profile: {e}")


# =============================
# FEEDBACK TAB
# =============================
with tab_feedback:

    st.subheader("Review Management")
    st.caption(
        "Feedback is invited from every guest. Negative feedback privately "
        "alerts the manager for service recovery — it never affects a guest's "
        "ability to post a public review."
    )

    # ---- Submit feedback ----
    st.markdown("### Submit Feedback")
    fb_name = st.text_input("Guest name", key="fb_name")
    fb_rating = st.slider("Rating", min_value=1, max_value=5, value=5, key="fb_rating")
    fb_comment = st.text_area("Comment", key="fb_comment")

    if st.button("Submit Feedback", key="fb_submit"):
        if not fb_name:
            st.warning("Enter a guest name first.")
        else:
            try:
                resp = requests.post(
                    f"{API_BASE}/feedback/{fb_name}",
                    json={"rating": fb_rating, "comment": fb_comment or None},
                    headers=HEADERS
                )
                res = resp.json()
                sentiment = res.get("sentiment")
                if sentiment == "negative":
                    st.error(
                        f"Recorded as **negative** — manager alerted "
                        f"({res.get('manager_alerted')})."
                    )
                else:
                    st.success(f"Recorded as **{sentiment}**.")
            except Exception as e:
                st.error(f"Could not submit feedback: {e}")

    st.divider()

    # ---- View feedback ----
    st.markdown("### Collected Feedback")
    try:
        resp = requests.get(f"{API_BASE}/feedback", headers=HEADERS)
        items = resp.json().get("feedback", [])

        if not items:
            st.info("No feedback submitted yet.")
        else:
            # Quick summary metrics
            ratings = [i["rating"] for i in items if i.get("rating") is not None]
            negatives = [i for i in items if i.get("sentiment") == "negative"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(items))
            with col2:
                st.metric("Avg rating", round(sum(ratings) / len(ratings), 2) if ratings else "—")
            with col3:
                st.metric("Negative", len(negatives))

            sentiment_icon = {"negative": "🔴", "positive": "🟢", "neutral": "⚪"}
            for i in items:
                icon = sentiment_icon.get(i.get("sentiment"), "⚪")
                rating = i.get("rating")
                rating_str = f"{rating}★" if rating is not None else "no rating"
                with st.expander(f"{icon} {i['guest_name']} · {rating_str} · {i.get('created_at', '')}"):
                    st.write(f"**Sentiment:** {i.get('sentiment')}")
                    st.write(f"**Comment:** {i.get('comment') or '(none)'}")
                    if i.get("manager_alerted"):
                        st.warning("Manager was alerted for service recovery.")
    except Exception as e:
        st.error(f"Could not load feedback: {e}")


# =============================
# ANALYTICS TAB
# =============================
with tab_analytics:

    st.subheader("Owner Analytics")
    st.caption("The ROI picture: workload handled, resolution speed, and guest sentiment.")

    # ---- Proactive insights (what's about to become a problem) ----
    st.markdown("### 🔎 Insights")
    try:
        ins = requests.get(f"{API_BASE}/insights", headers=HEADERS).json().get("insights", [])
        if not ins:
            st.success("No issues detected — operations look healthy.")
        else:
            sev_icon = {"high": "🔴", "medium": "🟠", "low": "🟡"}
            for item in ins:
                icon = sev_icon.get(item.get("severity"), "🔸")
                st.warning(f"{icon} {item.get('message')}")
    except Exception as e:
        st.error(f"Could not load insights: {e}")

    st.divider()

    try:
        resp = requests.get(f"{API_BASE}/analytics", headers=HEADERS)
        data = resp.json()
        t = data.get("tickets", {})
        f = data.get("feedback", {})

        st.markdown("### Tickets")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total", t.get("total", 0))
        with c2:
            st.metric("Resolved", t.get("resolved", 0))
        with c3:
            rate = t.get("resolution_rate_pct")
            st.metric("Resolution rate", f"{rate}%" if rate is not None else "—")
        with c4:
            st.metric("Escalated", t.get("escalated", 0))

        c5, c6, c7 = st.columns(3)
        with c5:
            st.metric("Open", t.get("open", 0))
        with c6:
            st.metric("In progress", t.get("in_progress", 0))
        with c7:
            mins = t.get("avg_resolution_minutes")
            st.metric("Avg resolution", f"{mins} min" if mins is not None else "—")

        st.divider()
        st.markdown("### Feedback")
        c8, c9, c10, c11 = st.columns(4)
        with c8:
            st.metric("Responses", f.get("total", 0))
        with c9:
            avg = f.get("avg_rating")
            st.metric("Avg rating", f"{avg} ★" if avg is not None else "—")
        with c10:
            st.metric("Positive", f.get("positive", 0))
        with c11:
            st.metric("Negative", f.get("negative", 0))

    except Exception as e:
        st.error(f"Could not load analytics: {e}")