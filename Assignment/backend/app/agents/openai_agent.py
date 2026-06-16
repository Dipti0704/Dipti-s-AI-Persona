import json
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List

from openai import OpenAI

from backend.app.config import settings
from backend.app.core.agent import BaseAgent
from backend.app.tools.calendar_tool import get_scheduler
from backend.app.tools.rag_tool import search_knowledge_base


def next_workday() -> str:
    target = datetime.today() + timedelta(days=1)
    while target.weekday() >= 5:
        target += timedelta(days=1)
    return target.strftime("%Y-%m-%d")


class MockLLMAgent(BaseAgent):
    """
    Offline fallback used when OPENAI_API_KEY is not configured.

    It still follows the same tool flow as the real agent, but it does not
    invent polished biography answers. For profile questions it returns
    retrieved RAG context so local demos remain grounded.
    """

    def __init__(self):
        self.scheduler = get_scheduler()

    def chat(self, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        msg_lower = user_message.lower()

        if any(word in msg_lower for word in ["slot", "availability", "available", "free"]):
            date_str = next_workday()
            for word in msg_lower.split():
                if "-" in word and len(word) == 10:
                    date_str = word

            slots = self.scheduler.get_available_slots(date_str)
            slot_lines = "\n".join([f"- {slot}" for slot in slots]) or "- No slots available"
            response = (
                f"I've checked Dipti's calendar for {date_str}. Her available interview slots are:\n"
                f"{slot_lines}\n\n"
                "Which slot works best for you? Please share your name, email, and preferred slot to book."
            )
            return {
                "response": response,
                "tool_calls": [{"name": "get_available_slots", "args": {"date": date_str}}],
            }

        if any(word in msg_lower for word in ["book", "schedule", "confirm"]):
            date_str = next_workday()
            time_str = "10:00"
            name = "Interviewer"
            email = "recruiter@company.com"

            for word in msg_lower.split():
                if ":" in word and len(word) == 5:
                    time_str = word
                if "@" in word:
                    email = word

            result = self.scheduler.book_slot(date_str, time_str, name, email)
            if result["status"] == "success":
                response = (
                    "Awesome, that interview slot is booked.\n"
                    f"- Date: {result['date']}\n"
                    f"- Time: {result['time']}\n"
                    f"- Meeting Link: {result['meeting_link']}\n\n"
                    f"{result['message']}"
                )
            else:
                response = f"I could not book that slot: {result['message']}"

            return {
                "response": response,
                "tool_calls": [
                    {
                        "name": "book_interview",
                        "args": {"date": date_str, "time": time_str, "name": name, "email": email},
                    }
                ],
            }

        context = search_knowledge_base(user_message, limit=2)
        if "No matching" in context:
            response = (
                "I couldn't find specific information about that in Dipti's records. "
                "To stay accurate, I prefer not to speculate. You can email Dipti directly at "
                "dipti820h@gmail.com."
            )
            return {"response": response, "tool_calls": []}

        response = (
            "Based on Dipti's verified records, here is the most relevant information I found:\n\n"
            f"{context[:900]}"
        )
        return {
            "response": response,
            "tool_calls": [{"name": "search_knowledge_base", "args": {"query": user_message}}],
        }

    def chat_stream(self, user_message: str, history: List[Dict[str, str]]) -> Generator[Dict[str, Any], None, None]:
        result = self.chat(user_message, history)
        if result.get("tool_calls"):
            yield {"tool_calls": result["tool_calls"]}
        
        words = result["response"].split(" ")
        for i, word in enumerate(words):
            suffix = " " if i < len(words) - 1 else ""
            yield {"text": word + suffix}


class OpenAIAgent(BaseAgent):
    """
    OpenAI tool-calling agent.

    It decides when to search verified knowledge, when to check availability,
    and when to book an interview.
    """

    def __init__(self):
        self.client = None
        self.scheduler = get_scheduler()
        self.mock_agent = MockLLMAgent()

        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as exc:
                print(f"Error starting OpenAI Agent client: {exc}")

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search Dipti's verified resume, skills, experience, and GitHub project data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "A natural language search query about projects, skills, education, or experience.",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_available_slots",
                    "description": "Return available calendar meeting times for a date in YYYY-MM-DD format.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Target date in YYYY-MM-DD format.",
                            }
                        },
                        "required": ["date"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "book_interview",
                    "description": "Book an interview slot on Dipti's calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Meeting date in YYYY-MM-DD format."},
                            "time": {"type": "string", "description": "Meeting time in HH:MM format."},
                            "name": {"type": "string", "description": "Interviewer's full name."},
                            "email": {"type": "string", "description": "Interviewer's email address."},
                        },
                        "required": ["date", "time", "name", "email"],
                    },
                },
            },
        ]

    def _get_system_prompt(self) -> str:
        return (
            "You are Dipti's AI Representative, a professional and natural conversational assistant.\n"
            "Your goals are to answer questions about Dipti Hatwar's background, skills, projects, "
            "and fit for the role, and to help book interview calls.\n\n"
            "Grounding rules:\n"
            "1. For questions about Dipti's background, education, experience, skills, or projects, "
            "first use the search_knowledge_base tool.\n"
            "2. Answer only from retrieved context. If the answer is not in retrieved context, say: "
            "'I do not have verified information on that topic in Dipti's records. To remain honest "
            "and avoid hallucination, I prefer not to guess. Feel free to contact Dipti directly at "
            "dipti820h@gmail.com!'\n"
            "3. Do not invent company names, degrees, dates, achievements, or personal details.\n"
            "4. Keep phone-style answers concise, usually 1-3 sentences.\n"
            "5. For availability, use get_available_slots. To confirm a chosen slot, use book_interview."
        )

    def _run_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name == "search_knowledge_base":
            return search_knowledge_base(args.get("query", ""))

        if name == "get_available_slots":
            date_str = args.get("date", "")
            slots = self.scheduler.get_available_slots(date_str)
            return json.dumps({"date": date_str, "available_slots": slots})

        if name == "book_interview":
            return json.dumps(
                self.scheduler.book_slot(
                    date_str=args.get("date", ""),
                    time_str=args.get("time", ""),
                    attendee_name=args.get("name", ""),
                    attendee_email=args.get("email", ""),
                )
            )

        return "Error: Unknown tool name."

    def chat(self, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        if not self.client:
            return self.mock_agent.chat(user_message, history)

        try:
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            messages.extend({"role": msg["role"], "content": msg["content"]} for msg in history)
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.2,
            )

            response_msg = response.choices[0].message
            tool_calls = response_msg.tool_calls
            if not tool_calls:
                return {"response": response_msg.content, "tool_calls": []}

            messages.append(response_msg)
            executed_tools = []

            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                result = self._run_tool(func_name, func_args)

                executed_tools.append({"name": func_name, "args": func_args})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result,
                    }
                )

            second_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2,
            )
            return {
                "response": second_response.choices[0].message.content,
                "tool_calls": executed_tools,
            }

        except Exception as exc:
            print(f"Error in OpenAI Agent chat: {exc}. Using mock agent fallback.")
            return self.mock_agent.chat(user_message, history)

    def chat_stream(self, user_message: str, history: List[Dict[str, str]]) -> Generator[Dict[str, Any], None, None]:
        if not self.client:
            yield from self.mock_agent.chat_stream(user_message, history)
            return

        try:
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            messages.extend({"role": msg["role"], "content": msg["content"]} for msg in history)
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.2,
                stream=True
            )

            tool_calls_dict = {}
            for chunk in response:
                delta = chunk.choices[0].delta
                
                # Check for content stream
                if delta.content:
                    yield {"text": delta.content}
                
                # Check for tool calls
                if delta.tool_calls:
                    for tc_chunk in delta.tool_calls:
                        idx = tc_chunk.index
                        if idx not in tool_calls_dict:
                            tool_calls_dict[idx] = {
                                "id": tc_chunk.id,
                                "name": tc_chunk.function.name if tc_chunk.function else "",
                                "arguments": tc_chunk.function.arguments if tc_chunk.function else ""
                            }
                        else:
                            if tc_chunk.id:
                                tool_calls_dict[idx]["id"] = tc_chunk.id
                            if tc_chunk.function:
                                if tc_chunk.function.name:
                                    tool_calls_dict[idx]["name"] += tc_chunk.function.name
                                if tc_chunk.function.arguments:
                                    tool_calls_dict[idx]["arguments"] += tc_chunk.function.arguments

            if tool_calls_dict:
                tool_calls = []
                for idx, tc in sorted(tool_calls_dict.items()):
                    tool_calls.append(tc)
                
                # Yield tool calls info to UI
                yield {"tool_calls": [{"name": tc["name"], "args": json.loads(tc["arguments"] or "{}")} for tc in tool_calls]}
                
                # Execute tool calls locally
                assistant_msg = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["arguments"]
                            }
                        } for tc in tool_calls
                    ]
                }
                messages.append(assistant_msg)
                
                for tc in tool_calls:
                    func_name = tc["name"]
                    func_args = json.loads(tc["arguments"] or "{}")
                    result = self._run_tool(func_name, func_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": func_name,
                        "content": result
                    })
                
                # Run the second API call to get the grounded response, streaming it
                second_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.2,
                    stream=True
                )
                for chunk in second_response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield {"text": delta.content}

        except Exception as exc:
            print(f"Error in OpenAI Agent chat_stream: {exc}. Using mock agent fallback.")
            yield from self.mock_agent.chat_stream(user_message, history)


def get_agent() -> BaseAgent:
    if settings.OPENAI_API_KEY:
        return OpenAIAgent()
    return MockLLMAgent()
