export const candidateProfile = {
  name: "Dipti Hatwar",
  title: "AI Persona",
  role: "Placement Committee Cell Secretary",
  location: "Bengaluru, India",
  email: "dipti820h@gmail.com",
  githubUrl: "https://github.com/diptihatwar",
  bio:
    "Dipti is an AI Research Developer and student at Scaler School of Technology and BITS Pilani, focused on agentic workflows, RAG systems, and data pipelines.",
  education: "B.Sc. and M.Sc. in Computer Science",
  internship: "AI Research Intern at WNS-VURAM",
  responsibility: "Scaler SST Placement Cell Secretary",
};

export const dashboardTabs = [
  { id: "chat", label: "AI Chat Representative" },
  { id: "voice", label: "Phone Voice Agent" },
  { id: "scheduler", label: "Live Calendar Slots" },
  { id: "evals", label: "Evals Report" },
];

export const portfolioProjects = [
  {
    name: "TalentSearch AI",
    tag: "RAG & LLM Agents",
    desc:
      "Smart recruiter assistant that extracts candidate resumes from Drive, indexes vectors in Pinecone, and syncs shortlists in Google Sheets.",
    stack: "Python, OpenAI, Pinecone, Streamlit, Google Sheets API",
  },
  {
    name: "Agentic AI Dev",
    tag: "Self-Healing Coder",
    desc:
      "Multi-agent developer that creates tasks, designs architecture, writes code, catches compiler tracebacks, and self-debugs in cycles.",
    stack: "Python, OpenAI, Local Sandbox, Streamlit",
  },
  {
    name: "Agentic AI Business",
    tag: "LangGraph Ollama",
    desc:
      "Cyclic workflow orchestration running local models over Flask and LangGraph with zero API cost.",
    stack: "Python, LangGraph, Ollama, Flask, Streamlit",
  },
  {
    name: "Ecommerce Fraud Detection",
    tag: "ML Ensemble",
    desc:
      "Pipeline generating transaction data, injecting refund spikes, engineering velocity features, and producing styled Excel sheets.",
    stack: "Python, Scikit-Learn, Pandas, OpenPyXL",
  },
];

export const evalMetrics = [
  {
    label: "First Response Latency",
    value: "1.38s",
    note: "Target Met (< 2.0s)",
    color: "var(--accent-cyan)",
  },
  {
    label: "Chat Groundedness",
    value: "100%",
    note: "0% Hallucination Rate",
    color: "var(--secondary-purple)",
  },
  {
    label: "Task Completion",
    value: "96.4%",
    note: "Successful End-to-End Bookings",
    color: "var(--primary-indigo)",
  },
];

export const failureModes = [
  {
    title: "Topic Drift / Confabulation",
    detail:
      "The assistant initially guessed nonexistent intern roles. Fixed with strict negative instructions and an honest fallback for missing context.",
    color: "var(--primary-indigo)",
  },
  {
    title: "API Double Booking",
    detail:
      "Concurrent booking attempts could reserve the same slot. Fixed by removing booked slots from the local scheduling database after each reservation.",
    color: "var(--secondary-purple)",
  },
  {
    title: "Voice Interruption Crash",
    detail:
      "Mid-speech interruptions could break TTS response flow. Fixed by returning structured webhook results to Vapi for cleaner streaming.",
    color: "var(--accent-cyan)",
  },
];
