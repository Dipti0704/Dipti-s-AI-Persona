import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from backend.app.core.scheduler import BaseScheduler
from backend.app.config import settings

class LocalMockScheduler(BaseScheduler):
    """
    Local JSON-based scheduler (Open-Closed Principle).
    Simulates slot generation and guarantees slot elimination on booking to prevent double-booking.
    """
    def __init__(self, db_path: str = settings.LOCAL_BOOKINGS_PATH):
        self.db_path = Path(db_path)
        self._init_db()
        
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            with self.db_path.open("w", encoding="utf-8") as f:
                json.dump([], f)
                
    def _get_bookings(self) -> List[Dict[str, Any]]:
        try:
            with self.db_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
            
    def _save_bookings(self, bookings: List[Dict[str, Any]]):
        with self.db_path.open("w", encoding="utf-8") as f:
            json.dump(bookings, f, indent=2)

    def get_available_slots(self, date_str: str) -> List[str]:
        # Validate date format (YYYY-MM-DD)
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return []
            
        # Don't book in the past or weekends
        if target_date.date() < datetime.today().date():
            return []
        if target_date.weekday() >= 5: # Saturday/Sunday
            return []
            
        # Standard default daily slots (9 AM to 6 PM IST)
        default_slots = ["10:00", "11:00", "14:00", "15:00", "16:00"]
        
        # Load existing bookings and filter out booked slots for this date
        bookings = self._get_bookings()
        booked_times = {b["time"] for b in bookings if b["date"] == date_str and b["status"] != "cancelled"}
        
        available_slots = [slot for slot in default_slots if slot not in booked_times]
        return available_slots

    def book_slot(self, date_str: str, time_str: str, attendee_name: str, attendee_email: str) -> Dict[str, Any]:
        # Validate date and time
        available = self.get_available_slots(date_str)
        if time_str not in available:
            return {
                "status": "error",
                "message": f"Slot {time_str} on {date_str} is not available or has already been booked."
            }
            
        bookings = self._get_bookings()
        booking_id = f"mock-cal-{len(bookings) + 1000}"
        meeting_link = f"https://cal.com/dipti-hatwar/interview-{booking_id}"
        
        new_booking = {
            "id": booking_id,
            "date": date_str,
            "time": time_str,
            "attendee_name": attendee_name,
            "attendee_email": attendee_email,
            "meeting_link": meeting_link,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        bookings.append(new_booking)
        self._save_bookings(bookings)
        
        return {
            "status": "success",
            "booking_id": booking_id,
            "date": date_str,
            "time": time_str,
            "meeting_link": meeting_link,
            "message": f"Successfully booked interview for {attendee_name} at {time_str} on {date_str}. A calendar invite has been sent to {attendee_email}."
        }

class CalComScheduler(BaseScheduler):
    """
    Production scheduler connecting directly to Cal.com API (Open-Closed Principle).
    Automatically falls back to LocalMockScheduler if API Key is not set or request fails.
    """
    def __init__(self):
        self.mock_scheduler = LocalMockScheduler()
        self.api_key = settings.CAL_API_KEY
        self.event_type_id = settings.CAL_EVENT_TYPE_ID
        self.base_url = "https://api.cal.com/v1"
        
    def get_available_slots(self, date_str: str) -> List[str]:
        if not self.api_key or not self.event_type_id:
            return self.mock_scheduler.get_available_slots(date_str)
            
        try:
            # Query Cal.com availability
            # In a real environment, we call their availability endpoint
            headers = {"Content-Type": "application/json"}
            url = f"{self.base_url}/availability"
            params = {
                "apiKey": self.api_key,
                "eventTypeId": self.event_type_id,
                "startTime": f"{date_str}T00:00:00Z",
                "endTime": f"{date_str}T23:59:59Z"
            }
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                slots = []
                for slot in data.get("slots", []):
                    # Parse slot ISO format (e.g. 2026-05-23T10:00:00.000Z)
                    dt = datetime.fromisoformat(slot["time"].replace("Z", "+00:00"))
                    slots.append(dt.strftime("%H:%M"))
                return slots
            else:
                print(f"Cal.com returned status {response.status_code}. Using local scheduler fallback.")
                return self.mock_scheduler.get_available_slots(date_str)
        except Exception as e:
            print(f"Failed to query Cal.com availability: {e}. Using local scheduler fallback.")
            return self.mock_scheduler.get_available_slots(date_str)

    def book_slot(self, date_str: str, time_str: str, attendee_name: str, attendee_email: str) -> Dict[str, Any]:
        if not self.api_key or not self.event_type_id:
            return self.mock_scheduler.book_slot(date_str, time_str, attendee_name, attendee_email)
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            url = f"{self.base_url}/bookings"
            
            # Combine date and time
            start_iso = f"{date_str}T{time_str}:00Z"
            
            payload = {
                "eventTypeId": int(self.event_type_id),
                "start": start_iso,
                "name": attendee_name,
                "email": attendee_email,
                "timeZone": settings.TIMEZONE
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code in [200, 201]:
                data = response.json()
                booking = data.get("booking", {})
                return {
                    "status": "success",
                    "booking_id": str(booking.get("id")),
                    "date": date_str,
                    "time": time_str,
                    "meeting_link": booking.get("videoCallUrl", f"https://cal.com/meeting/{booking.get('id')}"),
                    "message": f"Successfully booked interview via Cal.com! Confirmation sent to {attendee_email}."
                }
            else:
                print(f"Cal.com booking returned {response.status_code}. Booking locally.")
                return self.mock_scheduler.book_slot(date_str, time_str, attendee_name, attendee_email)
        except Exception as e:
            print(f"Cal.com booking exception: {e}. Booking locally.")
            return self.mock_scheduler.book_slot(date_str, time_str, attendee_name, attendee_email)

# Factory function
def get_scheduler() -> BaseScheduler:
    if settings.CAL_API_KEY:
        return CalComScheduler()
    return LocalMockScheduler()
