"""
IITIAN AI - Central Tool Registry
Unified interface for tool schemas, risk classification, and dispatch execution.
"""

import time
from backend.tools.alarm import set_alarm, list_alarms, delete_alarm, set_timer, list_timers, stop_timer
from backend.tools.calling import call_contact, get_contact, list_contacts, add_contact
from backend.tools.messaging import send_message
from backend.tools.calendar import add_event, get_upcoming_events, delete_event
from backend.tools.reminders import add_reminder, get_reminders, complete_reminder, delete_reminder
from backend.tools.weather import get_weather
from backend.tools.datetime_tool import get_current_datetime
from backend.tools.web_search import search_web
from backend.tools.calculator import calculate
from backend.tools.computer import open_application, set_volume, get_battery_status, take_screenshot, open_url
from backend.tools.files import search_project_or_file, list_recent_files
from backend.memory.memory_manager import memory_manager
from backend.monitoring.langsmith_tracer import tracer

TOOLS = {
    "set_alarm": {
        "function": set_alarm,
        "description": "Sets an alarm at a specific time with a label.",
        "risk": "MEDIUM",
        "parameters": {"time_str": "string (e.g. 07:00, 7 AM)", "label": "string", "repeat_days": "string"}
    },
    "list_alarms": {
        "function": list_alarms,
        "description": "Lists all active alarms.",
        "risk": "LOW",
        "parameters": {"status": "string (active/all)"}
    },
    "delete_alarm": {
        "function": delete_alarm,
        "description": "Cancels or deletes an alarm.",
        "risk": "HIGH",
        "parameters": {"alarm_id": "string"}
    },
    "set_timer": {
        "function": set_timer,
        "description": "Sets a countdown timer for a duration in seconds.",
        "risk": "MEDIUM",
        "parameters": {"duration_seconds": "integer", "label": "string"}
    },
    "list_timers": {
        "function": list_timers,
        "description": "Lists currently running countdown timers.",
        "risk": "LOW",
        "parameters": {}
    },
    "stop_timer": {
        "function": stop_timer,
        "description": "Stops or deletes a timer.",
        "risk": "LOW",
        "parameters": {"timer_id": "string"}
    },
    "call_contact": {
        "function": call_contact,
        "description": "Calls a contact from address book by name or relation.",
        "risk": "HIGH",
        "parameters": {"name": "string (e.g. Papa, Mom, Rahul)"}
    },
    "list_contacts": {
        "function": list_contacts,
        "description": "Lists all saved contacts.",
        "risk": "LOW",
        "parameters": {}
    },
    "add_contact": {
        "function": add_contact,
        "description": "Saves a new contact to the address book.",
        "risk": "MEDIUM",
        "parameters": {"name": "string", "phone": "string", "relation": "string"}
    },
    "send_message": {
        "function": send_message,
        "description": "Sends a message to a contact via WhatsApp or SMS.",
        "risk": "HIGH",
        "parameters": {"recipient": "string", "message": "string", "platform": "string"}
    },
    "add_calendar_event": {
        "function": add_event,
        "description": "Adds a meeting or event to the calendar.",
        "risk": "MEDIUM",
        "parameters": {"title": "string", "start_time": "string", "location": "string"}
    },
    "get_upcoming_events": {
        "function": get_upcoming_events,
        "description": "Retrieves upcoming calendar meetings and events.",
        "risk": "LOW",
        "parameters": {"days": "integer"}
    },
    "add_reminder": {
        "function": add_reminder,
        "description": "Sets a reminder for a specific task or time.",
        "risk": "MEDIUM",
        "parameters": {"text": "string", "remind_at": "string", "priority": "string"}
    },
    "get_reminders": {
        "function": get_reminders,
        "description": "Lists pending reminders and tasks.",
        "risk": "LOW",
        "parameters": {"status": "string"}
    },
    "complete_reminder": {
        "function": complete_reminder,
        "description": "Marks a reminder as completed.",
        "risk": "LOW",
        "parameters": {"reminder_id": "string"}
    },
    "get_weather": {
        "function": get_weather,
        "description": "Fetches current weather and forecast for any city.",
        "risk": "LOW",
        "parameters": {"city": "string"}
    },
    "get_current_datetime": {
        "function": get_current_datetime,
        "description": "Retrieves the real-time date, day of week, and 12-hour clock time.",
        "risk": "LOW",
        "parameters": {"query": "string"}
    },
    "search_web": {
        "function": search_web,
        "description": "Searches Wikipedia, DuckDuckGo, and live internet for questions.",
        "risk": "LOW",
        "parameters": {"query": "string"}
    },
    "calculate": {
        "function": calculate,
        "description": "Performs mathematical calculations, percentages, and unit conversions.",
        "risk": "LOW",
        "parameters": {"expression": "string"}
    },
    "open_application": {
        "function": open_application,
        "description": "Launches a desktop application (Chrome, VS Code, Terminal, Spotify).",
        "risk": "MEDIUM",
        "parameters": {"app_name": "string"}
    },
    "set_volume": {
        "function": set_volume,
        "description": "Sets the system sound volume level from 0 to 100.",
        "risk": "MEDIUM",
        "parameters": {"level": "integer"}
    },
    "get_battery_status": {
        "function": get_battery_status,
        "description": "Reads current battery percentage and charging state.",
        "risk": "LOW",
        "parameters": {}
    },
    "take_screenshot": {
        "function": take_screenshot,
        "description": "Captures a screenshot of the computer screen.",
        "risk": "MEDIUM",
        "parameters": {"filename": "string"}
    },
    "open_project": {
        "function": search_project_or_file,
        "description": "Finds a user's coding project or file and opens it in editor.",
        "risk": "MEDIUM",
        "parameters": {"name": "string"}
    },
    "remember_fact": {
        "function": lambda key, value: memory_manager.set_memory(key, value),
        "description": "Stores a personal fact, habit, or preference into long-term memory.",
        "risk": "MEDIUM",
        "parameters": {"key": "string", "value": "string"}
    },
    "recall_fact": {
        "function": lambda key: {"key": key, "value": memory_manager.get_memory(key)},
        "description": "Recalls a stored fact from long-term memory.",
        "risk": "LOW",
        "parameters": {"key": "string"}
    }
}

def execute_tool(tool_name: str, arguments: dict = None) -> dict:
    """Executes a registered tool with provided arguments safely."""
    if arguments is None:
        arguments = {}

    if tool_name not in TOOLS:
        return {"success": False, "error": f"Tool '{tool_name}' not registered."}

    tool_def = TOOLS[tool_name]
    func = tool_def["function"]
    start_t = time.time()

    try:
        # Call function with kwargs matching function signature
        result = func(**arguments)
        latency_ms = (time.time() - start_t) * 1000
        # Log to audit log & LangSmith
        memory_manager.log_audit(f"tool:{tool_name}", str(arguments), "success")
        tracer.trace_tool_execution(tool_name, arguments, result, latency_ms)
        return {"success": True, "tool": tool_name, "result": result, "latency_ms": round(latency_ms, 2)}
    except TypeError as te:
        # If parameters didn't match, try calling without args if empty
        try:
            result = func()
            latency_ms = (time.time() - start_t) * 1000
            tracer.trace_tool_execution(tool_name, arguments, result, latency_ms)
            return {"success": True, "tool": tool_name, "result": result, "latency_ms": round(latency_ms, 2)}
        except Exception as e:
            latency_ms = (time.time() - start_t) * 1000
            tracer.trace_tool_execution(tool_name, arguments, {"error": str(te)}, latency_ms)
            return {"success": False, "tool": tool_name, "error": f"Parameter error: {str(te)}"}
    except Exception as e:
        latency_ms = (time.time() - start_t) * 1000
        memory_manager.log_audit(f"tool:{tool_name}", str(arguments), f"error: {str(e)}")
        tracer.trace_tool_execution(tool_name, arguments, {"error": str(e)}, latency_ms)
        return {"success": False, "tool": tool_name, "error": str(e)}

def get_tools_manifest() -> list:
    """Returns schemas of all available tools."""
    manifest = []
    for name, d in TOOLS.items():
        manifest.append({
            "name": name,
            "description": d["description"],
            "risk": d["risk"],
            "parameters": d["parameters"]
        })
    return manifest
