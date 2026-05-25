import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Pinecone settings (optional, will fall back to local RAG if not configured)
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "resumes-index")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")
    
    # Calendar settings (optional, will fall back to local bookings.json if not configured)
    CAL_API_KEY: str = os.getenv("CAL_API_KEY", "")
    CAL_EVENT_TYPE_ID: str = os.getenv("CAL_EVENT_TYPE_ID", "")
    
    # Server settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Representative Bio
    REPRESENTATIVE_NAME: str = "Dipti's AI Persona"
    CANDIDATE_NAME: str = "Dipti Hatwar"
    CANDIDATE_EMAIL: str = "dipti820h@gmail.com"
    CANDIDATE_PHONE: str = "+91-8446447324"
    
    # Default availability rules (9 AM to 6 PM IST)
    AVAILABLE_HOURS_START: int = 9  # 9 AM
    AVAILABLE_HOURS_END: int = 18   # 6 PM
    TIMEZONE: str = "Asia/Kolkata"

settings = Settings()
