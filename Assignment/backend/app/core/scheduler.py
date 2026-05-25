from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScheduler(ABC):
    """
    Abstract Base Class for Calendar Scheduling (Open-Closed Principle).
    Allows plugging in Cal.com, Google Calendar, or LocalMockScheduler seamlessly.
    """
    
    @abstractmethod
    def get_available_slots(self, date_str: str) -> List[str]:
        """
        Retrieve a list of available time slots for a given date (format: YYYY-MM-DD).
        Returns slots as a list of strings (format: HH:MM).
        """
        pass
        
    @abstractmethod
    def book_slot(self, date_str: str, time_str: str, attendee_name: str, attendee_email: str) -> Dict[str, Any]:
        """
        Book a specific slot for a date and time.
        Returns a dictionary containing confirmation details (e.g. status, event link, booking ID).
        """
        pass
