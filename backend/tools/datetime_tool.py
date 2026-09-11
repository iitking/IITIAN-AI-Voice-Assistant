"""
IITIAN AI - Date & Time Intelligence Tool
Provides current real-time date, day, month, year, and 12-hour clock time.
"""

from datetime import datetime

def get_current_datetime(query: str = "") -> dict:
    """
    Returns current date, day, month, year, and time.
    """
    now = datetime.now()
    
    # Formats
    date_str = now.strftime("%A, %B %d, %Y")      # e.g., Wednesday, October 07, 2026
    date_short = now.strftime("%d %B %Y")          # e.g., 07 October 2026
    time_str = now.strftime("%I:%M %p")            # e.g., 10:42 PM
    day_name = now.strftime("%A")                  # e.g., Wednesday
    import re
    query_lower = query.lower()
    if any(k in query_lower for k in ["time", "samay", "baje"]):
        voice_resp = f"Abhi time {time_str} ho raha hai."
        msg = f"The current time is {time_str} ({date_short})."
    elif any(k in query_lower for k in ["date", "tarikh", "taarikh"]):
        voice_resp = f"Aaj ki date {date_str} hai."
        msg = f"Today's date is {date_str}."
    elif re.search(r'\b(?:day|din|vaar)\b', query_lower) and "date" not in query_lower:
        voice_resp = f"Aaj {day_name} hai ({date_short})."
        msg = f"Today is {day_name}, {date_short}."
    else:
        # Date or general
        voice_resp = f"Aaj ki date {date_str} hai, aur time {time_str} ho raha hai."
        msg = f"Today is {date_str}. The current time is {time_str}."

    return {
        "success": True,
        "date": date_str,
        "time": time_str,
        "day": day_name,
        "message": msg,
        "voice_response": voice_resp
    }
