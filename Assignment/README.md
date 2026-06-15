# Dipti's AI Persona

This project is an AI representative for Dipti Hatwar. It supports:

- grounded chat using resume and project knowledge
- calendar slot checking and interview booking
- a Vapi/Twilio voice webhook path
- a React dashboard for recruiters
- a small evaluation script for groundedness and latency checks

The main engineering idea is simple: the assistant should answer personal/career questions only from verified knowledge, and should use tools when it needs to search knowledge or book meetings.

## How The System Works

```text
Recruiter UI / Voice Call
        |
        v
FastAPI routes in backend/app/api
        |
        v
Agent in backend/app/agents/openai_agent.py
        |
        +--> RAG search tool in backend/app/tools/rag_tool.py
        |       |
        |       v
        |   Knowledge chunks from backend/app/knowledge
        |
        +--> Calendar tool in backend/app/tools/calendar_tool.py
                |
                v
            Cal.com, or local backend/data/bookings.json fallback
```

## Folder Map

```text
Assignment/
|
|-- backend/
|   |-- run.py                         # Starts the FastAPI server
|   |-- requirements.txt               # Python dependencies
|   |-- data/                          # Local runtime data such as bookings.json
|   `-- app/
|       |-- main.py                    # Creates FastAPI app and registers routers
|       |-- config.py                  # Environment variables and default settings
|       |-- api/                       # HTTP endpoints
|       |   |-- chat.py                # POST /api/chat
|       |   |-- calendar.py            # POST /api/slots and /api/book
|       |   `-- voice.py               # POST /api/voice-webhook for Vapi tools
|       |-- agents/
|       |   `-- openai_agent.py        # Main agent, tool routing, mock fallback
|       |-- core/                      # Interfaces for agent, scheduler, vector store
|       |-- knowledge/                 # Verified resume/project data used by RAG
|       `-- tools/                     # Tool functions the agent can call
|
|-- frontend/
|   |-- package.json                   # React/Vite dependencies and scripts
|   `-- src/
|       |-- App.jsx                    # Dashboard controller and tab switching
|       |-- index.css                  # Shared UI styles
|       |-- content/profile.js         # Candidate/project/evaluation display content
|       `-- components/
|           |-- ChatWidget.jsx         # Chat UI connected to /api/chat
|           |-- Scheduler.jsx          # Calendar booking UI
|           `-- VoiceCall.jsx          # Vapi web-call UI
|
|-- evals/
|   `-- evaluate.py                    # Automated checks for key assignment metrics
|
`-- Evals_Report.md                    # Written evaluation report
```

## Backend Setup

```bash
cd Assignment/backend
pip install -r requirements.txt
python run.py
```

The API runs at `http://localhost:8000`.

Optional environment variables can be placed in `Assignment/backend/.env`:

```env
OPENAI_API_KEY=your_openai_key
CAL_API_KEY=your_cal_key
CAL_EVENT_TYPE_ID=your_event_type_id
LOCAL_BOOKINGS_PATH=data/bookings.json
```

Without `OPENAI_API_KEY`, the app uses `MockLLMAgent` so the project still runs locally.
Without Cal.com credentials, bookings are stored locally in `backend/data/bookings.json`.

## Frontend Setup

```bash
cd Assignment/frontend
npm install
npm run dev
```

The dashboard runs at `http://localhost:3000`.

Optional frontend environment variables:

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_VAPI_PUBLIC_KEY=your_vapi_public_key
VITE_VAPI_ASSISTANT_ID=your_vapi_assistant_id
```

If Vapi variables are missing, the voice panel shows that setup is required instead of pretending a live call is configured.

## Evaluation

```bash
cd Assignment
python evals/evaluate.py
```

The evaluator checks:

- whether important facts are answered from the knowledge base
- whether out-of-scope questions receive an honest fallback
- average response latency
- whether the RAG tool was called when expected

## What To Explain In A Demo

1. `backend/app/knowledge` stores the verified data about Dipti.
2. `backend/app/tools/rag_tool.py` exposes that data as a searchable agent tool.
3. `backend/app/agents/openai_agent.py` decides whether to search knowledge, check slots, or book an interview.
4. `backend/app/api` turns those agent capabilities into HTTP endpoints.
5. `frontend/src/components` gives each feature its own UI: chat, scheduler, and voice.
6. `frontend/src/content/profile.js` keeps display-only profile/project text separate from component logic.
