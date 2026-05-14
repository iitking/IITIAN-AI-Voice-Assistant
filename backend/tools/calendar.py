"""
IITIAN AI - Smart Calendar Tool
Provides scheduling, event lookups, and calendar management.
"""

import uuid
import datetime
from backend.memory.storage import storage

def add_event(title: str, start_time: str, end_time: str = "", location: str = "", description: str = "") -> dict:
    """
    Schedules an event in the calendar.
    start_time can be format 'YYYY-MM-DD HH:MM' or relative like 'tomorrow 11:00'.
    """
    event_id = str(uuid.uuid4())[:8]
    now_iso = datetime.datetime.now().isoformat()

    # Normalize relative dates
    clean_time = _parse_datetime_str(start_time)

    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO calendar_events (id, title, start_time, end_time, location, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event_id, title.strip(), clean_time, end_time.strip(), location.strip(), description.strip(), now_iso))
        conn.commit()

    return {
        "success": True,
        "event_id": event_id,
        "title": title,
        "start_time": clean_time,
        "location": location,
        "message": f"Event '{title}' scheduled for {clean_time}."
    }

def get_upcoming_events(days: int = 7) -> list:
    """Returns calendar events scheduled for upcoming days."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, start_time, end_time, location, description, created_at
            FROM calendar_events
            ORDER BY start_time ASC
        """)
        return [dict(r) for r in cursor.fetchall()]

def delete_event(event_id: str) -> dict:
    """Cancels or deletes an event."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calendar_events WHERE id = ? OR LOWER(title) LIKE ?", (event_id, f"%{event_id.lower()}%"))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": f"Event deleted successfully."}
        return {"success": False, "message": f"Event '{event_id}' not found."}

def _parse_datetime_str(date_str: str) -> str:
    """Simple parser converting relative keywords (tomorrow, today) into ISO-like date string."""
    now = datetime.datetime.now()
    lower = date_str.lower()
    time_part = "10:00"
    
    # Try finding time like '11 AM', '11:00', '7 PM'
    words = lower.split()
    for w in words:
        if ":" in w:
            time_part = w
            break
        elif w.isdigit() and int(w) <= 24:
            time_part = f"{w.zfill(2)}:00"

    if "tomorrow" in lower or "kal" in lower:
        target_date = now + datetime.timedelta(days=1)
    elif "today" in lower or "aaj" in lower:
        target_date = now
    else:
        return date_str

    return f"{target_date.strftime('%Y-%m-%d')} {time_part}"
