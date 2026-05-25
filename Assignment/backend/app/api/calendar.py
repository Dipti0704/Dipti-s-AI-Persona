from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.app.tools.calendar_tool import get_scheduler

router = APIRouter()
scheduler = get_scheduler()

class SlotRequest(BaseModel):
    date: str

class BookingPayload(BaseModel):
    date: str
    time: str
    name: str
    email: str

@router.post("/slots")
async def get_slots_endpoint(payload: SlotRequest):
    try:
        slots = scheduler.get_available_slots(payload.date)
        return {"date": payload.date, "slots": slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book")
async def book_slot_endpoint(payload: BookingPayload):
    try:
        res = scheduler.book_slot(
            date_str=payload.date,
            time_str=payload.time,
            attendee_name=payload.name,
            attendee_email=payload.email
        )
        if res["status"] == "success":
            return res
        else:
            raise HTTPException(status_code=400, detail=res["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
