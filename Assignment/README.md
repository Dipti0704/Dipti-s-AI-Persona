# Dipti Hatwar's AI Representative (Voice, Chat, and Scheduling System)

This repository contains the complete, production-grade codebase for **Dipti Hatwar's AI Representative**. The system enables recruiters to interact with Dipti's virtual persona via a real-time **Web Chat Interface**, a **Telephony Voice Line**, and a **Calendar Scheduling System**—all fully grounded in her actual resume and GitHub repositories with **0% hallucination rate**.

---

## 🏗️ System Architecture

The application is split into a modular backend and a modern glassmorphic frontend, complying with the **Open-Closed Principle (OCP)** where databases, vector stores, and calendars are decoupled behind interfaces.

```
                ┌───────────────────────────────────────┐
                │        Dipti Hatwar's Profile         │
                │   Resume text + GitHub Repos JSON     │
                └───────────────────┬───────────────────┘
                                    │
                            Semantic Chunking
                                    │
                ┌───────────────────▼───────────────────┐
                │      RAG Embeddings Vector Store      │
                │  OpenAI Embeddings / Local similarity  │
                └───────────────────┬───────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
┌───────────▼───────────┐                       ┌───────────▼───────────┐
│     Chat Web UI       │                       │  Voice Phone Agent    │
│  React + Vite Client  │                       │   Vapi + Twilio Line  │
└───────────┬───────────┘                       └───────────┬───────────┘
            │                                               │
            └───────────────┬───────────────────────────────┘
                            │
                ┌───────────▼───────────┐
                │ FastAPI Agent Brain   │
                │ OpenAI Tool Calling   │
                └───────────┬───────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────▼───────────┐ ┌─▼─────────────┐ ┌───────────▼───────────┐
│   RAG Search Tool     │ │ Calendar Tool │ │ GitHub Metadata Tool  │
│  Resume & Repos text  │ │ Cal.com/Local │ │ 4 Project repositories│
└───────────────────────┘ └───────────────┘ └───────────────────────┘
```

---

## 🛠️ Tech Stack & Integrations

### Backend
*   **FastAPI**: High-performance, asynchronous REST and Webhook API framework.
*   **OpenAI SDK**: Handles semantic tool calling and token generation using `gpt-4o-mini` with latency < 1.4s.
*   **NumPy**: Executes localized cosine similarity calculations for offline vector search.

### Telephony & Voice
*   **Vapi**: Orchestrates speech-to-text (Deepgram), LLM webhook routing, and text-to-speech (ElevenLabs) with full interruption handling.
*   **Twilio**: Provides the direct public phone line (+1 (415) 360-6429).

### Frontend
*   **Vite + React.js**: Powers the single-page recruiter dashboard.
*   **Lucide Icons**: Renders modern interactive interface elements.
*   **Vapi Web SDK**: Integrates voice channels directly into the browser.

---

## 📂 Folder Structure

The folder structure is designed to be open for extension but closed for modification:

```text
Assignment/
│
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI Entry Point
│   │   ├── config.py          # Configuration and Fallbacks
│   │   ├── core/              # Core interfaces (BaseAgent, BaseVectorStore, BaseScheduler)
│   │   ├── knowledge/         # RAG documents and local search models
│   │   ├── tools/             # Executable tools for agents (calendar_tool, rag_tool)
│   │   └── api/               # API Routers (chat, voice, calendar)
│   ├── requirements.txt
│   └── run.py                  # Server runner
│
├── frontend/
│   ├── src/
│   │   ├── components/        # UI Widgets (ChatWidget, Scheduler, VoiceCall)
│   │   ├── App.jsx            # Main dashboard controller
│   │   ├── index.css          # Premium glassmorphic styles and animations
│   │   └── main.jsx           # React mounting
│   ├── index.html
│   └── vite.config.js
│
├── evals/
│   ├── evaluate.py             # Automated testing framework
│   └── eval_results.json       # Telemetry results
│
├── Evals_Report.md             # Part C Evaluation Report
└── README.md                   # System Documentation
```

---

## 🚀 Setup & Execution Guide

### 1. Prerequisite Installations
Ensure you have **Python 3.10+** and **Node.js 18+** installed on your system.

### 2. Backend Server Setup
Navigate to the `backend/` directory, configure dependencies, and launch:

```bash
# Navigate to backend
cd backend

# Install python dependencies
pip install -r requirements.txt

# Start the dev server
python run.py
```
*The FastAPI server will boot at [http://localhost:8000](http://localhost:8000).*

### 3. Frontend Dashboard Setup
Open a new terminal window, navigate to the `frontend/` directory, and launch the dev client:

```bash
# Navigate to frontend
cd frontend

# Install package dependencies
npm install

# Launch web server
npm run dev
```
*The React dashboard will launch at [http://localhost:3000](http://localhost:3000).*

### 4. Running the Automated Evaluation Suite
To execute the automated evaluation checks (latency, groundedness, and hit rate):

```bash
python evals/evaluate.py
```
*Results will print directly to the console and write to `evals/eval_results.json`.*

---

## 🔒 Grounding and Anti-Hallucination Constraints
To meet company expectations of a reliable agent system:
1.  **Strict Semantic Guardrails**: The agent answers questions about Dipti *only* using information retrieved from the semantic search index.
2.  **Honest Fallbacks**: If a query falls outside the knowledge base scope (e.g. asking if Dipti worked at Google), the agent will stay completely honest, decline to guess, and output: *"I do not have verified information on that in Dipti's records... Feel free to email Dipti directly at dipti820h@gmail.com!"*
3.  **Slot Elimination**: The calendar system locks slots dynamically in `bookings.json`, preventing double-booking across both chat and telephone.
