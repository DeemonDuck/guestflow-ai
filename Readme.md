# GuestFlow AI — README.md

# 🏨 GuestFlow AI

GuestFlow AI is an event-driven hospitality workflow automation platform built using FastAPI, Streamlit, SQLite, RAG architecture, and local LLM inference via Ollama.

The system automates hotel guest workflows across:

* Pre-Stay Operations
* In-Stay Guest Support
* Post-Stay Follow-Up

It uses a multi-agent orchestration architecture to route events dynamically and simulate real-world hospitality automation systems.

---

# 🚀 Features

## ✅ Event-Driven Workflow Orchestration

* Webhook-based event ingestion
* Intelligent routing system
* Multi-agent architecture

## ✅ AI-Powered Guest Support

* Local LLM inference using Ollama + Phi-3
* Conversational hotel assistant
* Context-aware responses

## ✅ RAG (Retrieval Augmented Generation)

* Hotel FAQ knowledge base
* Retrieval-based contextual support
* Dynamic query handling

## ✅ Workflow Intelligence

* VIP guest prioritization
* Escalation handling
* Urgent request detection

## ✅ Persistent CRM Memory

* SQLite database integration
* Guest history tracking
* Stateful workflow handling

## ✅ Visual Dashboard

* Streamlit workflow monitoring UI
* Real-time workflow execution
* AI response visualization

---

# 🧠 System Architecture

![GuestFlow AI Architecture](assets/architecture.png)

---

# 📊 Dashboard Preview

## Dashboard Home

![Dashboard Home](assets/dashboard_home.png)

---

## Standard Guest Workflow

### API Response

![Standard Response](assets/dashboard_standard_response.png)

### Workflow Analysis

![Standard Analysis](assets/dashboard_standard_analysis.png)

---

## VIP Escalation Workflow

### API Response

![Escalation Response](assets/dashboard_escalation_response.png)

### Workflow Analysis

![Escalation Analysis](assets/dashboard_escalation_analysis.png)

# 🛠️ Tech Stack

| Component    | Technology                        |
| ------------ | --------------------------------- |
| Backend API  | FastAPI                           |
| Dashboard    | Streamlit                         |
| Database     | SQLite                            |
| AI Framework | LangChain Compatible Architecture |
| Local LLM    | Ollama + Phi-3                    |
| RAG Layer    | Custom Retrieval Pipeline         |
| Language     | Python                            |

---

# 📂 Project Structure

```text
guestflow-ai/
│
├── agents/
│   ├── orchestrator.py
│   ├── prestay_agent.py
│   ├── instay_agent.py
│   └── poststay_agent.py
│
├── tools/
│   ├── email_tool.py
│   ├── crm_tool.py
│   └── ticket_tool.py
│
├── rag/
│   ├── hotel_FAQ.txt
│   └── rag_service.py
│
├── database/
│   └── db.py
│
├── dashboard.py
├── llm_service.py
├── main.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Setup Instructions

# 1. Clone Repository

```bash
git clone https://github.com/DeemonDuck/guestflow-ai.git
```

```bash
cd guestflow-ai
```

---

# 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 3. Install Ollama

Download Ollama:
[https://ollama.com/download](https://ollama.com/download)

---

# 4. Pull Phi-3 Model

```bash
ollama pull phi3
```

---

# 5. Start Ollama Server

```bash
ollama serve
```

---

# 6. Start FastAPI Backend

```bash
uvicorn main:app --reload
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

# 7. Start Streamlit Dashboard

```bash
streamlit run dashboard.py
```

Dashboard URL:

```text
http://localhost:8501
```

---

# 🧪 Sample Workflow Payloads

## Booking Confirmation

```json
{
  "event_type": "booking_confirmed",
  "guest_name": "Rahul"
}
```

---

## Guest Request

```json
{
  "event_type": "guest_request",
  "guest_name": "Rahul",
  "guest_question": "Can I get late checkout tomorrow?"
}
```

---

## Escalation Workflow

```json
{
  "event_type": "guest_request",
  "guest_name": "Priya",
  "guest_question": "I want refund for bad service"
}
```

---

# 🎫 Ticket Management API

Guest requests that need follow-up are stored as **tickets** so they can be
tracked through their full lifecycle: `open → in_progress → resolved`.

## List Tickets

```text
GET /tickets               # all tickets
GET /tickets?status=open   # filter by status
```

## Update Ticket Status

```text
PATCH /tickets/{ticket_id}
```

```json
{
  "status": "in_progress"
}
```

Allowed statuses: `open`, `in_progress`, `resolved`.

When a ticket is moved to `resolved`, GuestFlow automatically follows up with the
guest to confirm the issue is actually fixed — closing the loop from request to
resolution. (The follow-up fires only on the transition into `resolved`, so
re-saving a resolved ticket never spams the guest.)

## Escalation Timer

Open tickets that sit unattended too long can be surfaced and escalated to a
manager:

```text
GET  /tickets/escalations?minutes=30        # list stale open tickets (read-only)
POST /tickets/escalations/run?minutes=30     # alert manager about stale tickets
```

Each ticket is escalated at most once (tracked via an `escalated` flag), so
running the escalation repeatedly never re-notifies the same ticket. Point a
scheduler/cron at the `run` endpoint to make escalation automatic.

Staff can also view and update tickets visually from the **🎫 Tickets** tab in
the Streamlit dashboard (filter by status, then change a ticket's state inline).

---

# 👤 Guest Profiles & Preferences

GuestFlow keeps a durable **profile** per guest so repeat visitors are recognised
and personalised — instead of asking the same questions every stay.

A profile stores:

| Field           | Example                              |
| --------------- | ------------------------------------ |
| `contact_email` | `sharma@example.com`                 |
| `preferences`   | `High floor, extra pillows, veg meal`|
| `is_vip`        | `true`                               |
| `notes`         | `Anniversary on 12 Aug`              |

Profiles are saved via a **merge upsert**: updating one field never erases the
others, so partial updates are safe. When a guest has a profile, their stored
preferences are injected into the AI prompt for both booking confirmations
(pre-stay) and in-stay requests, so replies are personalised automatically.

VIP prioritisation is **driven by the profile's `is_vip` flag** (no hardcoded
guest list): when a VIP guest raises an in-stay request, the workflow enables
priority handling automatically.

## Profile API

```text
GET  /profiles/{guest_name}     # read a profile (null if none exists)
POST /profiles/{guest_name}     # create or update (merge upsert)
DELETE /profiles/{guest_name}   # erase a guest's PII (right-to-erasure)
```

```json
{
  "contact_email": "sharma@example.com",
  "preferences": "High floor, extra pillows",
  "is_vip": true,
  "notes": "Anniversary on 12 Aug"
}
```

Staff can also manage profiles visually from the **👤 Profiles** tab in the
Streamlit dashboard: look up a guest by name, and the form pre-fills with any
existing profile so preferences, VIP status and notes can be edited and saved.

---

# ⭐ Review Management

After checkout, GuestFlow asks every guest for feedback and helps the hotel
protect its rating — **without** any practice that would violate review
platform policies.

## How it works

* Every guest receives a feedback request that includes the public review link
  (when `REVIEW_LINK` is configured). The invitation is **never** conditioned on
  how the guest rates their stay.
* When a guest submits **negative** feedback (a low rating, or a comment with
  negative wording), the manager is privately alerted so they can recover the
  experience quickly.
* That alert is an internal operations signal only — it never blocks, hides or
  diverts the guest's ability to post a public review.

> ⚠️ **Compliance:** selectively soliciting public reviews only from happy
> guests ("review gating") violates Google's review policies and FTC guidance.
> GuestFlow intentionally offers the review invitation to **all** guests; the
> sentiment check is used solely to trigger internal service recovery.

## Feedback API

```text
GET  /feedback                 # list all submitted feedback
POST /feedback/{guest_name}     # submit a rating (1-5) and/or a comment
```

```json
{
  "rating": 2,
  "comment": "The room was not clean."
}
```

Ratings at or below `REVIEW_ALERT_THRESHOLD` (default `3`) flag the feedback as
negative and alert the manager.

Staff can submit and review feedback from the **⭐ Feedback** tab in the
Streamlit dashboard, which shows total/average rating, a negative count, and
flags entries where the manager was alerted.

---

# 🔎 Proactive Insights

Beyond answering guests, GuestFlow watches the data it collects and surfaces
patterns a busy manager would otherwise miss:

```text
GET /insights
```

* **Systemic issues** — a cluster of similar tickets in the same area/time
  window (e.g. "3 'Maintenance' tickets on floor 3 in 24h — likely one root
  cause").
* **Repeat rooms** — a single room generating many tickets.
* **Feedback themes** — a topic recurring across negative reviews (e.g.
  "'cleanliness' came up in 3 negative reviews").

These appear at the top of the **📊 Analytics** dashboard tab. The pitch: *most
hotel AI answers your guests — GuestFlow tells you what's about to become a
problem.*

## Manager Daily Digest

GuestFlow can compose a short operations briefing (ticket counts, escalations,
average rating, recent feedback, and the insights above) and email it to the
manager:

```text
GET  /digest          # preview the digest body without sending
POST /digest/run       # compose and email it to MANAGER_EMAIL
```

Point a scheduler/cron at `POST /digest/run` to deliver a "morning brief"
automatically.

---

# 📊 Owner Analytics

A single ROI view for the hotel owner, aggregated from the data GuestFlow
already collects:

```text
GET /analytics
```

Returns ticket metrics (total, open / in-progress / resolved, resolution rate,
average resolution time in minutes, escalations) and feedback metrics (total
responses, average rating, positive / negative counts).

The **📊 Analytics** tab in the Streamlit dashboard renders these as at-a-glance
metric cards — the "here's what you're paying for" screen.

---

# 🔐 Security

GuestFlow has been hardened against common API and data-handling risks:

* **Authentication** — `API_KEY` (sent as `X-API-Key`) is checked in
  constant time. Set `REQUIRE_AUTH=true` in production so the server refuses to
  start without a key (fail-closed). Interactive docs (`/docs`, `/openapi.json`)
  are disabled automatically when a key is configured.
* **Input validation** — request bodies are validated (email format, rating
  `1–5`, length limits) before any processing.
* **Email safety** — values placed in email headers are stripped of CR/LF and
  recipients are format-validated, preventing header injection.
* **Rate limiting** — abusable/expensive endpoints (`/webhook`, `/feedback`,
  `/digest/run`, `/tickets/escalations/run`) are throttled per client IP.
* **Prompt-injection** — untrusted guest text is fenced and the model is
  instructed to treat it as data, never as commands.
* **Right to erasure** — `DELETE /profiles/{guest_name}` removes a guest's
  profile and feedback and anonymizes their tickets.

> ⚠️ **Deployment requirements:** always run behind **HTTPS/TLS** (the API key
> and guest data travel in requests/responses), and set `API_KEY` +
> `REQUIRE_AUTH`. SQLite uses WAL mode for safer concurrency, but a real
> multi-hotel deployment should move to **Postgres** and add **encryption at
> rest** for guest PII.

---

# ⚙️ Configuration

GuestFlow reads its settings from environment variables (e.g. a `.env` file):

| Variable                            | Purpose                                              |
| ----------------------------------- | ---------------------------------------------------- |
| `GMAIL_SENDER` / `GMAIL_APP_PASSWORD` | Mailbox used to send notifications                 |
| `GMAIL_RECIPIENT`                   | Default mailbox (fallback when no specific recipient)|
| `MANAGER_EMAIL`                     | Where escalation alerts go (falls back to `GMAIL_RECIPIENT`) |
| `HOTEL_NAME`                        | Hotel name used in guest messaging                   |
| `ESCALATION_MINUTES`                | Default staleness threshold for escalations (default `30`) |
| `LLM_MODEL` / `LLM_TEMPERATURE`     | Ollama model + temperature (default `phi3` / `0.5`)  |
| `API_KEY`                           | If set, all API requests must send it as the `X-API-Key` header |
| `REQUIRE_AUTH`                      | If `true`, the server refuses to start without `API_KEY` (fail-closed) |
| `REVIEW_LINK`                       | Public review URL included in every guest feedback request |
| `REVIEW_ALERT_THRESHOLD`            | Ratings at/below this (1-5) alert the manager (default `3`) |

Notifications are routed automatically: **guest-facing messages** (booking
confirmation and resolved-ticket follow-up) go to the guest's stored
`contact_email`, while **escalation alerts** go to `MANAGER_EMAIL`. Each falls
back to `GMAIL_RECIPIENT` when a specific address isn't on file.

## API Authentication

When `API_KEY` is set, every endpoint requires the matching key in an
`X-API-Key` request header (missing/incorrect keys get `401`). When `API_KEY`
is **unset**, authentication is disabled for local development and the server
prints a warning at startup. **Always set `API_KEY` before exposing the API on
a network.** The Streamlit dashboard reads `API_KEY` from the environment and
sends it automatically.

---

# 🌱 Demo Data

To make the dashboard look alive for a demo, seed realistic sample data
(profiles, tickets in every state, and feedback):

```bash
python seed_demo.py
```

It is non-destructive — profiles are merge-upserted and ticket/feedback seeding
is skipped if demo data already exists, so it is safe to re-run.

---

# 🧪 Tests

A `pytest` suite covers the core behaviour: ticket lifecycle (creation,
status validation, resolve follow-up firing once, escalation alerting once),
guest profile merge-upsert, review/feedback sentiment + compliance (review link
offered to every guest, manager alerted only on negative feedback), analytics
aggregation, and API key authentication.

```bash
pytest tests/ -q
```

Tests run against an isolated temporary database (no impact on `guestflow.db`)
and stub all outbound email, so the suite sends nothing and touches no real data.

---

# 🎯 Key Concepts Demonstrated

* AI Workflow Automation
* Event-Driven Systems
* Multi-Agent Architecture
* Retrieval Augmented Generation (RAG)
* Local LLM Inference
* Workflow Orchestration
* Persistent State Management
* Hospitality CRM Automation

---

# 📌 Future Improvements

* WhatsApp / SMS notifications (via a Business Solution Provider)
* LangChain Tool Calling Agents
* Cloud Deployment
* Real CRM/PMS Integration
* Multi-tenant support (per-hotel configuration & data isolation)
* Advanced Semantic Vector Search

---

# 👨‍💻 Author

Developed by Ridham Taneja
