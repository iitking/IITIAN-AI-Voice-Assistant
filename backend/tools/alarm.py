"""
IITIAN AI - Alarm and Timer Tools
Provides alarm and countdown timer creation, listing, cancellation, and active checking.
"""

import uuid
import time
import datetime
from backend.memory.storage import storage

def set_alarm(time_str: str, label: str = "Alarm", repeat_days: str = "") -> dict:
    """
    Sets an alarm for a specific time.
    time_str can be in format '07:00', '7:00 AM', '19:30', or relative like 'in 10 minutes'.
    """
    alarm_id = str(uuid.uuid4())[:8]
    now = datetime.datetime.now().isoformat()
    
    # Clean time representation
    clean_time = time_str.strip()
    
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alarms (id, time_str, label, repeat_days, status, created_at)
            VALUES (?, ?, ?, ?, 'active', ?)
        """, (alarm_id, clean_time, label, repeat_days, now))
        conn.commit()

    return {
        "success": True,
        "alarm_id": alarm_id,
        "time": clean_time,
        "label": label,
        "repeat": repeat_days or "Once",
        "message": f"Alarm set for {clean_time} ({label})"
    }

def list_alarms(status: str = "active") -> list:
    """Lists alarms with specified status."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        if status == "all":
            cursor.execute("SELECT id, time_str, label, repeat_days, status, created_at FROM alarms ORDER BY time_str")
        else:
            cursor.execute("SELECT id, time_str, label, repeat_days, status, created_at FROM alarms WHERE status = ? ORDER BY time_str", (status,))
        return [dict(row) for row in cursor.fetchall()]

def delete_alarm(alarm_id: str) -> dict:
    """Deletes or cancels an alarm by ID or matching time."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alarms WHERE id = ? OR time_str = ?", (alarm_id, alarm_id))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": f"Alarm {alarm_id} cancelled successfully."}
        return {"success": False, "message": f"No alarm found matching '{alarm_id}'."}

def set_timer(duration_seconds: int, label: str = "Timer") -> dict:
    """
    Sets a countdown timer for a given duration in seconds.
    """
    timer_id = str(uuid.uuid4())[:8]
    now_ts = time.time()
    ends_at = now_ts + duration_seconds
    now_iso = datetime.datetime.now().isoformat()

    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO timers (id, duration, label, ends_at, status, created_at)
            VALUES (?, ?, ?, ?, 'active', ?)
        """, (timer_id, duration_seconds, label, ends_at, now_iso))
        conn.commit()

    mins = duration_seconds // 60
    secs = duration_seconds % 60
    duration_human = f"{mins} min {secs} sec" if mins > 0 else f"{secs} sec"

    return {
        "success": True,
        "timer_id": timer_id,
        "duration": duration_seconds,
        "duration_human": duration_human,
        "ends_at": ends_at,
        "label": label,
        "message": f"Timer of {duration_human} started for {label}."
    }

def list_timers(status: str = "active") -> list:
    """Lists active countdown timers and calculates remaining seconds."""
    now_ts = time.time()
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, duration, label, ends_at, status, created_at FROM timers WHERE status = ? ORDER BY ends_at ASC", (status,))
        rows = cursor.fetchall()
        timers = []
        for r in rows:
            d = dict(r)
            remaining = max(0, int(d["ends_at"] - now_ts))
            d["remaining_seconds"] = remaining
            d["is_finished"] = remaining == 0
            timers.append(d)
        return timers

def stop_timer(timer_id: str) -> dict:
    """Stops or deletes a timer."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE timers SET status = 'cancelled' WHERE id = ?", (timer_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": f"Timer {timer_id} stopped."}
        return {"success": False, "message": f"No active timer found with id {timer_id}."}

def dismiss_timer(timer_id: str = "") -> dict:
    """Marks an expired timer or all finished timers as completed."""
    now_ts = time.time()
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        if timer_id:
            cursor.execute("UPDATE timers SET status = 'completed' WHERE id = ?", (timer_id,))
        else:
            cursor.execute("UPDATE timers SET status = 'completed' WHERE ends_at <= ? AND status = 'active'", (now_ts,))
        conn.commit()
        return {"success": True, "message": "Timer dismissed successfully."}

