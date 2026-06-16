from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator

class BaseAgent(ABC):
    """
    Abstract Base Class for the Agent Orchestration (Open-Closed Principle).
    Allows plugging in OpenAI Tool Calling agent, LangChain agent, or LangGraph stateflow seamlessly.
    """
    
    @abstractmethod
    def chat(self, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Processes a user message along with history and returns the agent's response.
        Response contains:
          - "response": text output
          - "tool_calls": list of tools executed (if any)
        """
        pass
        
    @abstractmethod
    def chat_stream(self, user_message: str, history: List[Dict[str, str]]) -> Generator[Dict[str, Any], None, None]:
        """
        Processes a user message and yields response packets in real time.
        Useful for high-end web streaming interfaces.
        """
        pass
