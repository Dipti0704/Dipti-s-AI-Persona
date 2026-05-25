from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.app.agents.openai_agent import get_agent

router = APIRouter()
agent = get_agent()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

class ChatResponse(BaseModel):
    response: str
    tool_calls: List[Dict[str, Any]] = []

@router.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    try:
        # Convert history format
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in payload.history]
        
        # Run agent
        result = agent.chat(payload.message, formatted_history)
        
        return {
            "response": result["response"],
            "tool_calls": result.get("tool_calls", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
