from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import chat, voice, calendar
from backend.app.config import settings

app = FastAPI(
    title=settings.REPRESENTATIVE_NAME,
    description="Grounded AI Persona for Dipti Hatwar's Recruiter Assistant.",
    version="1.0.0"
)

# Configure CORS for seamless web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local and server testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(voice.router, prefix="/api", tags=["Voice"])
app.include_router(calendar.router, prefix="/api", tags=["Calendar"])

@app.get("/")
def read_root():
    return {
        "status": "online",
        "agent": settings.REPRESENTATIVE_NAME,
        "candidate": settings.CANDIDATE_NAME,
        "details": "FastAPI Webhook & Chat service is running successfully."
    }
