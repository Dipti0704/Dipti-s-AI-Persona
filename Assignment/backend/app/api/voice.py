from fastapi import APIRouter, Request, Response
import json
from backend.app.tools.rag_tool import search_knowledge_base
from backend.app.tools.calendar_tool import get_scheduler

router = APIRouter()
scheduler = get_scheduler()

@router.post("/voice-webhook")
async def voice_webhook_endpoint(request: Request):
    """
    Vapi/Twilio Custom Tool Webhook (Open-Closed Principle).
    Receives function executions from Vapi real-time telephony agent,
    runs local RAG or calendar bookings, and returns formatted responses.
    """
    try:
        body = await request.json()
        print(f"Received Vapi Event: {json.dumps(body, indent=2)}")
        
        # Check event type
        msg = body.get("message", {})
        msg_type = msg.get("type")
        
        # Vapi is requesting a Tool / Function Call execution
        if msg_type == "tool-calls":
            tool_calls = msg.get("toolCalls", [])
            results = []
            
            for tc in tool_calls:
                tc_id = tc.get("id")
                func = tc.get("function", {})
                func_name = func.get("name")
                args = func.get("arguments", {})
                
                print(f"Voice tool requested: {func_name} with args: {args}")
                
                # Execute mapped tool
                if func_name == "search_knowledge_base":
                    result = search_knowledge_base(args.get("query", ""))
                elif func_name == "get_available_slots":
                    date_str = args.get("date", "")
                    slots = scheduler.get_available_slots(date_str)
                    result = f"Available slots for {date_str} are: " + ", ".join(slots)
                elif func_name == "book_interview":
                    res = scheduler.book_slot(
                        date_str=args.get("date", ""),
                        time_str=args.get("time", ""),
                        attendee_name=args.get("name", "Voice Caller"),
                        attendee_email=args.get("email", "recruiter-call@scaler.com")
                    )
                    if res["status"] == "success":
                        result = f"Booking successful! Your interview is confirmed for {res['time']} on {res['date']}. An invite was sent to {args.get('email')}."
                    else:
                        result = f"Failed to book: {res['message']}"
                else:
                    result = "Error: Mapped function not found."
                    
                results.append({
                    "toolCallId": tc_id,
                    "result": result
                })
                
            return {"results": results}
            
        # Standard acknowledgement response for other lifecycle events (e.g. call started, finished)
        return Response(status_code=200)
        
    except Exception as e:
        print(f"Error in Voice Webhook: {e}")
        return {"error": str(e)}
