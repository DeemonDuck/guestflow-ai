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
│   ├── hotel_faq.txt
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

## Profile API

```text
GET  /profiles/{guest_name}     # read a profile (null if none exists)
POST /profiles/{guest_name}     # create or update (merge upsert)
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

* Real Email/SMS Integration
* LangChain Tool Calling Agents
* Cloud Deployment
* Real CRM/PMS Integration
* Authentication Layer
* Advanced Semantic Vector Search

---

# 👨‍💻 Author

Developed by Ridham Taneja
