import json
from typing import List, Dict, Any, Generator
from openai import OpenAI
from backend.app.core.agent import BaseAgent
from backend.app.config import settings
from backend.app.tools.rag_tool import search_knowledge_base
from backend.app.tools.calendar_tool import get_scheduler

class MockLLMAgent(BaseAgent):
    """
    Mock Agent that simulates LLM reasoning and tool-calling when no OpenAI key is set.
    Allows zero-setup running and perfect offline local evaluation.
    """
    def __init__(self):
        self.scheduler = get_scheduler()

    def chat(self, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        msg_lower = user_message.lower()
        
        # Simple rule-based mock router
        if "slot" in msg_lower or "availability" in msg_lower or "available" in msg_lower or "free" in msg_lower:
            # Extract date if present, otherwise default to today
            date_str = "2026-05-25" # Example upcoming Monday
            for word in msg_lower.split():
                if "-" in word and len(word) == 10: # YYYY-MM-DD format
                    date_str = word
            slots = self.scheduler.get_available_slots(date_str)
            response = f"I've checked Dipti's calendar for {date_str}. Her available interview slots are:\n" + "\n".join([f"- {s}" for s in slots]) + "\n\nWhich slot works best for you? (Please provide your name, email, and preferred slot to book!)"
            return {"response": response, "tool_calls": [{"name": "get_available_slots", "args": {"date": date_str}}]}
            
        elif "book" in msg_lower or "schedule" in msg_lower or "confirm" in msg_lower:
            # Simulated booking
            date_str = "2026-05-25"
            time_str = "10:00"
            name = "Interviewer"
            email = "recruiter@company.com"
            
            # Simple extractor
            for word in msg_lower.split():
                if ":" in word and len(word) == 5:
                    time_str = word
                if "@" in word:
                    email = word
                    
            res = self.scheduler.book_slot(date_str, time_str, name, email)
            if res["status"] == "success":
                response = f"Awesome! I've booked that interview slot. Details:\n- Date: {res['date']}\n- Time: {res['time']}\n- Meeting Link: {res['meeting_link']}\n\n{res['message']}"
            else:
                response = f"Oops: {res['message']}"
            return {"response": response, "tool_calls": [{"name": "book_interview", "args": {"date": date_str, "time": time_str, "name": name, "email": email}}]}
            
        else:
            # Grounded RAG Search mockup
            context = search_knowledge_base(user_message, limit=2)
            
            # If nothing returned or empty query
            if "No matching" in context:
                response = "I couldn't find specific information regarding that in Dipti's records. To keep my response accurate, I prefer not to speculate. You are welcome to email Dipti directly at dipti820h@gmail.com!"
                return {"response": response, "tool_calls": []}
                
            # Simulate a summary response based on context
            if "WNS-VURAM" in context or "intern" in context or "experience" in msg_lower:
                response = "Dipti completed a 5-month internship as an AI Research Developer Intern at WNS-VURAM (March 2025 – July 2025). There, she built an automated BRD-to-Jira pipeline with priority extraction, conducted feasibility analyses on Firecrawl (FIRE-1 agent), and designed multi-agent workflows using LangGraph and UiPath."
            elif "talentsearch" in context or "project" in msg_lower:
                response = "Dipti built 'TalentSearch AI', an AI-powered hiring assistant using RAG and LLM agents for semantic resume retrieval, ranking, and analysis. It integrates Streamlit, OpenAI, and Pinecone, updating shortlisted candidates to Google Sheets."
            else:
                response = f"Based on Dipti's verified resume:\n{context[:300]}..."
                
            return {"response": response, "tool_calls": [{"name": "search_knowledge_base", "args": {"query": user_message}}]}

    def chat_stream(self, user_message: str, history: List[Dict[str, str]]) -> Generator[str, None, None]:
        res = self.chat(user_message, history)
        # Yield the response in small chunks to simulate streaming
        words = res["response"].split(" ")
        for word in words:
            yield word + " "

class OpenAIAgent(BaseAgent):
    """
    OpenAI-driven tool-calling agent (Open-Closed Principle).
    Coordinates conversation flow, decides when to run RAG or calendar booking tools, and enforces 100% honesty bounds.
    """
    def __init__(self):
        self.client = None
        self.scheduler = get_scheduler()
        
        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"Error starting OpenAI Agent client: {e}")
                
        # Fallback agent
        self.mock_agent = MockLLMAgent()
        
        # Tools definitions for OpenAI Function Calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Searches Dipti's resume, experience, skills, and detailed GitHub repositories for specific info.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The natural language search query focusing on projects, skills, or experience."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_available_slots",
                    "description": "Queries available calendar meeting times for a specific date (format: YYYY-MM-DD).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "The target date for the booking check, in YYYY-MM-DD format."
                            }
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_interview",
                    "description": "Books an interview slot for a specific date and time on Dipti's calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "The date of the meeting, in YYYY-MM-DD format."
                            },
                            "time": {
                                "type": "string",
                                "description": "The time slot to book, in HH:MM format (e.g. 10:00)."
                            },
                            "name": {
                                "type": "string",
                                "description": "The full name of the interviewer."
                            },
                            "email": {
                                "type": "string",
                                "description": "The email address of the interviewer."
                            }
                        },
                        "required": ["date", "time", "name", "email"]
                    }
                }
            }
        ]
        
    def _get_system_prompt(self) -> str:
        return (
            "You are Dipti's AI Representative, a professional, polished, and natural-sounding conversational assistant.\n"
            "Your goal is to introduce yourself, answer questions about Dipti Hatwar's background, skills, and fit for the role, and book interview calls.\n\n"
            "CRITICAL CONSTRAINTS FOR 100% HONESTY & ANTI-HALLUCINATION:\n"
            "1. You must answer questions about Dipti's background, education, experience, and projects ONLY using information retrieved from the 'search_knowledge_base' tool.\n"
            "2. If the user asks a question about Dipti that is not available in the retrieved context or knowledge base, say: "
            "'I do not have verified information on that topic in Dipti's records. To remain honest and avoid hallucination, I prefer not to guess. Feel free to contact Dipti directly at dipti820h@gmail.com!'\n"
            "3. DO NOT speculate or invent any details about Dipti's experience, company names, degrees, or personal life. If it is not explicitly stated in the retrieved documents, treat it as unknown.\n"
            "4. Speak naturally, elegantly, and concisely. Keep voice telephone answers shorter (1-3 sentences) so it flows like a normal phone conversation.\n"
            "5. You can propose booking an interview slot. If the interviewer asks for availability, call the 'get_available_slots' tool. Once they select a slot, call the 'book_interview' tool to confirm it end-to-end."
        )

    def chat(self, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        if not self.client:
            return self.mock_agent.chat(user_message, history)
            
        try:
            # Construct message thread
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})
            
            # Step 1: Initial call to check for tool calls
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.2
            )
            
            response_msg = response.choices[0].message
            tool_calls = response_msg.tool_calls
            
            if not tool_calls:
                return {
                    "response": response_msg.content,
                    "tool_calls": []
                }
                
            # Step 2: Execute tool calls and feed back to model
            messages.append(response_msg)
            executed_tools = []
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                # Executing designated tool
                if func_name == "search_knowledge_base":
                    result = search_knowledge_base(func_args.get("query", ""))
                elif func_name == "get_available_slots":
                    date_str = func_args.get("date", "")
                    slots = self.scheduler.get_available_slots(date_str)
                    result = json.dumps({"date": date_str, "available_slots": slots})
                elif func_name == "book_interview":
                    result = json.dumps(self.scheduler.book_slot(
                        date_str=func_args.get("date", ""),
                        time_str=func_args.get("time", ""),
                        attendee_name=func_args.get("name", ""),
                        attendee_email=func_args.get("email", "")
                    ))
                else:
                    result = "Error: Unknown tool name."
                    
                executed_tools.append({"name": func_name, "args": func_args})
                
                # Add tool response to messages thread
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                })
                
            # Call OpenAI again with the tool response context
            second_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2
            )
            
            return {
                "response": second_response.choices[0].message.content,
                "tool_calls": executed_tools
            }
            
        except Exception as e:
            print(f"Error in OpenAI Agent chat: {e}. Using mock agent fallback.")
            return self.mock_agent.chat(user_message, history)

    def chat_stream(self, user_message: str, history: List[Dict[str, str]]) -> Generator[str, None, None]:
        # For simplicity, if tool calling is triggered we resolve synchronously and stream the final answer
        # If no tool calling, we stream. For absolute reliability, we execute the tools synchronously and stream the final text
        res = self.chat(user_message, history)
        words = res["response"].split(" ")
        for word in words:
            yield word + " "

def get_agent() -> BaseAgent:
    if settings.OPENAI_API_KEY:
        return OpenAIAgent()
    return MockLLMAgent()
