"""
IITIAN AI - Smart Reminders Tool
Manages priority reminders, upcoming tasks, and completion tracking.
"""

import uuid
import datetime
from backend.memory.storage import storage
from backend.tools.calendar import _parse_datetime_str

def add_reminder(text: str, remind_at: str, priority: str = "medium") -> dict:
    """
    Creates a new reminder.
    remind_at can be 'tomorrow 10:00', '8 PM', 'today 18:00', etc.
    """
    reminder_id = str(uuid.uuid4())[:8]
    now_iso = datetime.datetime.now().isoformat()
    clean_time = _parse_datetime_str(remind_at)

    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (id, text, remind_at, priority, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (reminder_id, text.strip(), clean_time, priority.lower(), now_iso))
        conn.commit()

    return {
        "success": True,
        "reminder_id": reminder_id,
        "text": text,
        "remind_at": clean_time,
        "priority": priority,
        "message": f"Reminder set: '{text}' at {clean_time}."
    }

def get_reminders(status: str = "pending") -> list:
    """Lists reminders filtered by status (pending, completed, all)."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        if status == "all":
            cursor.execute("SELECT id, text, remind_at, priority, status, created_at FROM reminders ORDER BY remind_at ASC")
        else:
            cursor.execute("SELECT id, text, remind_at, priority, status, created_at FROM reminders WHERE status = ? ORDER BY remind_at ASC", (status,))
        return [dict(r) for r in cursor.fetchall()]

def complete_reminder(reminder_id: str) -> dict:
    """Marks a reminder as completed."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET status = 'completed' WHERE id = ? OR LOWER(text) LIKE ?", (reminder_id, f"%{reminder_id.lower()}%"))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": f"Reminder marked as completed."}
        return {"success": False, "message": f"Reminder not found."}

def delete_reminder(reminder_id: str) -> dict:
    """Deletes a reminder permanently."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ? OR LOWER(text) LIKE ?", (reminder_id, f"%{reminder_id.lower()}%"))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": f"Reminder removed."}
        return {"success": False, "message": f"Reminder not found."}
