"""
IITIAN AI - Intent Classification & Entity Extraction
Understands English, Hindi, and Hinglish natural language commands.
"""

import re
import datetime

def classify_intent(text: str) -> dict:
    """
    Classifies user utterance into primary intent and extracts tool parameters.
    """
    cleaned = text.strip()
    lower = cleaned.lower()

    # 1. Alarms: "kal subah 7 baje ka alarm laga do", "set an alarm for 7 AM", "wake me up at 6"
    if any(k in lower for k in ["alarm", "wake me up", "jaga dena", "utha dena"]):
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\d{1,2}\s*baje)', lower)
        time_str = "07:00"
        if time_match:
            time_raw = time_match.group(1).replace("baje", "").strip()
            if "pm" in time_raw or "shaam" in lower or "raat" in lower:
                nums = re.findall(r'\d+', time_raw)
                if nums:
                    val = int(nums[0])
                    time_str = f"{(val + 12 if val < 12 else val):02d}:00"
            else:
                nums = re.findall(r'\d+', time_raw)
                if nums:
                    val = int(nums[0])
                    time_str = f"{val:02d}:00"
        
        label = "Morning Alarm" if "subah" in lower or "morning" in lower else "Alarm"
        return {
            "intent": "set_alarm",
            "tool": "set_alarm",
            "arguments": {"time_str": time_str, "label": label},
            "confidence": 0.95
        }

    # 2. Timers: "set a 20-minute timer", "5 minute ka timer", "stopwatch"
    if any(k in lower for k in ["timer", "stopwatch"]):
        num_match = re.search(r'(\d+)\s*(?:minute|min|sec|second|ghanta|hour)', lower)
        duration = 600  # 10 mins default
        if num_match:
            val = int(num_match.group(1))
            if "sec" in lower:
                duration = val
            elif "hour" in lower or "ghanta" in lower:
                duration = val * 3600
            else:
                duration = val * 60
        return {
            "intent": "set_timer",
            "tool": "set_timer",
            "arguments": {"duration_seconds": duration, "label": "Timer"},
            "confidence": 0.95
        }

    # 3. Calling: "Papa ko call lagao", "call Mom", "call Rahul", "phone lagao"
    if any(k in lower for k in ["call", "phone lagao", "call karo", "call lagana"]):
        target = "Papa"
        words = lower.replace("ko", "").replace("call", "").replace("lagao", "").replace("karo", "").replace("phone", "").split()
        for w in words:
            if w not in ["please", "hey", "iitian", "mujhe", "mera", "meri"]:
                target = w.capitalize()
                break
        return {
            "intent": "call_contact",
            "tool": "call_contact",
            "arguments": {"name": target},
            "confidence": 0.95
        }

    # 4. Messaging: "Papa ko message karo ki main 8 baje aaunga", "message Rahul that I will be late"
    if any(k in lower for k in ["message", "msg", "sms", "whatsapp"]):
        recipient = "Papa"
        message_text = "Hello!"

        # Extract recipient
        to_match = re.search(r'(?:to|ko)\s+([a-zA-Z]+)', lower)
        if to_match and to_match.group(1) not in ["message", "bhejo", "karo"]:
            recipient = to_match.group(1).capitalize()
        else:
            first_word = lower.split()[0]
            if first_word not in ["message", "send", "bhejo", "whatsapp"]:
                recipient = first_word.capitalize()

        # Extract message content
        if " ki " in lower:
            message_text = cleaned.split(" ki ", 1)[1]
        elif " that " in lower:
            message_text = cleaned.split(" that ", 1)[1]
        else:
            msg_match = re.search(r'(?:message|msg|whatsapp)\s+(?:to\s+)?\w+\s+(.*)', cleaned, re.IGNORECASE)
            if msg_match:
                message_text = msg_match.group(1)

        return {
            "intent": "send_message",
            "tool": "send_message",
            "arguments": {"recipient": recipient, "message": message_text, "platform": "whatsapp"},
            "confidence": 0.92
        }

    # 5. Reminders: "kal 10 baje professor ko email yaad dilana", "remind me to study at 8 PM"
    if any(k in lower for k in ["remind", "yaad dilana", "yaad dila do", "reminder"]):
        time_part = "tomorrow 10:00" if any(k in lower for k in ["kal", "tomorrow"]) else "today 18:00"
        task_text = cleaned
        # Strip assistant prefixes
        for p in ["remind me to ", "remind me about ", "yaad dila do ki ", "yaad dilana "]:
            if p in lower:
                idx = lower.find(p) + len(p)
                task_text = cleaned[idx:]
                break

        return {
            "intent": "add_reminder",
            "tool": "add_reminder",
            "arguments": {"text": task_text.strip(), "remind_at": time_part, "priority": "medium"},
            "confidence": 0.95
        }

    # 6. Calendar: "schedule a meeting tomorrow at 11 AM", "kal 11 baje meeting add karo"
    if any(k in lower for k in ["schedule", "meeting", "calendar", "event"]):
        return {
            "intent": "add_calendar_event",
            "tool": "add_calendar_event",
            "arguments": {"title": "Scheduled Meeting", "start_time": "tomorrow 11:00", "location": "Online"},
            "confidence": 0.90
        }

    # 7. Weather: "what is the weather", "mausam kaisa hai", "will it rain", "barish hogi kya"
    if any(k in lower for k in ["weather", "mausam", "rain", "barish", "temperature", "tapman", "forecast"]):
        city = "Jaipur"
        # Extract city if mentioned
        for c in ["Delhi", "Jaipur", "Roorkee", "Mumbai", "Bengaluru", "Kolkata", "Pune", "Hyderabad", "Noida", "Gurugram"]:
            if c.lower() in lower:
                city = c
                break
        return {
            "intent": "get_weather",
            "tool": "get_weather",
            "arguments": {"city": city},
            "confidence": 0.95
        }

    # 7.5 Date & Time Intelligence: "today date", "what is the date", "current time", "aaj konsa din hai", "time kya hua"
    date_time_triggers = [
        "today date", "today's date", "current date", "what is the date", "what's the date",
        "date kya hai", "aaj ki date", "aaj date", "tarikh kya", "taarikh",
        "current time", "what time", "what is the time", "what's the time", "time kya hua",
        "time kya hai", "time kya ho raha", "samay kya", "kya samay", "kitne baje", "clock time",
        "konsa din", "kaun sa din", "what day is today", "what day is it", "today day", "aaj ka din", "day kya hai"
    ]
    is_date_time = (
        any(k in lower for k in date_time_triggers) or
        (any(w in lower for w in ["date", "tarikh", "taarikh"]) and not any(w in lower for w in ["meeting", "schedule", "calendar", "event", "alarm", "timer"])) or
        (lower in ["date", "time", "today", "day", "clock", "aaj kya hai", "aaj"]) or
        ("today" in lower and any(w in lower for w in ["date", "day", "time"]))
    )
    if is_date_time:
        return {
            "intent": "get_current_datetime",
            "tool": "get_current_datetime",
            "arguments": {"query": cleaned},
            "confidence": 0.98
        }

    # 8. Project Finding / Files: "mera laptop price predictor project open karo", "open my python project"
    if any(k in lower for k in ["project", "mera project", "open project", "repository", "repo"]):
        proj_name = "laptop price predictor"
        m = re.search(r'(?:open|kholo|show)?\s*(?:my|mera)?\s*(?:project|repo)?\s*([a-zA-Z0-9\s_-]+?)(?:\s*project|\s*kholo|\s*open|$)', lower)
        if m and len(m.group(1).strip()) > 3:
            proj_name = m.group(1).strip()
        return {
            "intent": "open_project",
            "tool": "open_project",
            "arguments": {"name": proj_name},
            "confidence": 0.94
        }

    # 9. System / Computer Apps: "open VS Code", "open Chrome", "Chrome kholo", "open Terminal"
    if any(k in lower for k in ["open", "kholo", "launch", "chalao"]):
        app_candidates = ["chrome", "google chrome", "vs code", "vscode", "terminal", "spotify", "calculator", "notes", "finder", "safari"]
        for app in app_candidates:
            if app in lower:
                return {
                    "intent": "open_application",
                    "tool": "open_application",
                    "arguments": {"app_name": app},
                    "confidence": 0.95
                }

    # 10. Volume Control: "set volume to 80", "volume 50 percent karo"
    if "volume" in lower or "sound" in lower or "awaz" in lower:
        num_m = re.search(r'(\d+)', lower)
        lvl = int(num_m.group(1)) if num_m else 50
        return {
            "intent": "set_volume",
            "tool": "set_volume",
            "arguments": {"level": lvl},
            "confidence": 0.95
        }

    # 11. Battery Status: "battery kitni hai", "check battery", "battery status"
    if any(k in lower for k in ["battery", "charging", "charge"]):
        return {
            "intent": "get_battery_status",
            "tool": "get_battery_status",
            "arguments": {},
            "confidence": 0.95
        }

    # 12. Screenshot: "screenshot lo", "take a screenshot"
    if "screenshot" in lower:
        return {
            "intent": "take_screenshot",
            "tool": "take_screenshot",
            "arguments": {},
            "confidence": 0.98
        }

    # 13. Calculator & Conversions: "165*92", "165/3", "calculate 250 * 48", "convert 10 km to miles", "cgpa percentage"
    has_arithmetic_expr = bool(re.search(r'\d+\s*[\+\-\*\/\^\%x×÷]\s*\d+', lower))
    has_math_keywords = any(k in lower for k in ["calculate", "hisab", "hisaab", "multiply", "divide", "% of", "cgpa", "convert", "km to", "miles to", "celsius", "fahrenheit", "square root", "sqrt"])
    has_hindi_math = bool(re.search(r'\d+\s*(?:into|guna|gunna|gune|bhag|bhaag|jod|jodo|ghatao|plus|minus)\s*\d+', lower))
    has_math_func = bool(re.search(r'(?:sqrt|sin|cos|tan|log|pow)\s*\(', lower))
    is_math_query = (has_arithmetic_expr or has_math_keywords or has_hindi_math or has_math_func) and not any(k in lower for k in ["alarm", "timer", "volume", "sound", "meeting", "call", "battery", "remind", "baje"])

    if is_math_query:
        expr = cleaned
        # Strip conversational prefixes
        expr = re.sub(r'^(?:what is|what\'s|calculate|compute|solve|tell me|batao|how much is|value of)\s+', '', expr, flags=re.IGNORECASE)
        # Strip conversational suffixes
        expr = re.sub(r'\s+(?:kitna hota hai|kitna hoga|batao|answer batao|kya hoga|kya hai)\s*$', '', expr, flags=re.IGNORECASE)
        expr = expr.rstrip('?=').strip()
        # Normalize Hindi/English math words to operators
        expr_normalized = re.sub(r'\s+(?:multiplied by|into|guna|gunna|gune|times|×)\s+', '*', expr, flags=re.IGNORECASE)
        expr_normalized = re.sub(r'\s+(?:divided by|divide by|bhag|bhaag|÷)\s+', '/', expr_normalized, flags=re.IGNORECASE)
        expr_normalized = re.sub(r'\s+(?:plus|jodo|jod)\s+', '+', expr_normalized, flags=re.IGNORECASE)
        expr_normalized = re.sub(r'\s+(?:minus|ghatao)\s+', '-', expr_normalized, flags=re.IGNORECASE)
        
        return {
            "intent": "calculate",
            "tool": "calculate",
            "arguments": {"expression": expr_normalized},
            "confidence": 0.98
        }

    # 14. Long-Term Memory (Store): "my name is Nivesh", "mera naam Nivesh hai", "remember my college is IIT"
    if any(k in lower for k in ["my name is", "mera naam", "remember", "yaad rakhna ki", "i like", "mera college"]):
        if "name" in lower or "naam" in lower:
            name_m = re.search(r'(?:my name is|mera naam)\s+([a-zA-Z\s]+?)(?:\s*hai|$)', cleaned, re.IGNORECASE)
            name_val = name_m.group(1).strip() if name_m else "Nivesh"
            return {
                "intent": "remember_fact",
                "tool": "remember_fact",
                "arguments": {"key": "user_name", "value": name_val},
                "confidence": 0.96
            }
        elif "college" in lower:
            return {
                "intent": "remember_fact",
                "tool": "remember_fact",
                "arguments": {"key": "college", "value": "IIT"},
                "confidence": 0.95
            }
        else:
            return {
                "intent": "remember_fact",
                "tool": "remember_fact",
                "arguments": {"key": "user_note", "value": cleaned},
                "confidence": 0.90
            }

    # 15. Assistant Identity & Capabilities: "who are you", "tum kaun ho", "what can you do", "who created you"
    assistant_info_triggers = [
        "who are you", "tum kaun ho", "what is your name", "tumhara naam",
        "who created you", "who made you", "tumhe kisne banaya", "tumhara creator", "kisne banaya",
        "what can you do", "kya kar sakte ho", "tum kya kya kar sakte ho", "features", "capabilities",
        "help me", "madad karo"
    ]
    if any(k in lower for k in assistant_info_triggers):
        sub_type = "capabilities"
        if any(k in lower for k in ["created", "made", "kisne banaya", "creator", "developer"]):
            sub_type = "creator"
        elif any(k in lower for k in ["who are you", "tum kaun ho", "your name", "tumhara naam"]):
            sub_type = "identity"
            
        return {
            "intent": "assistant_info",
            "tool": None,
            "arguments": {"type": sub_type},
            "confidence": 0.99
        }

    # 16. Long-Term Memory (Recall User Facts): "what is my name", "mera naam kya hai", "who am i", "main kaun hoon", "what do you remember"
    if any(k in lower for k in ["what is my name", "mera naam kya hai", "who am i", "main kaun hoon", "what do you remember"]):
        if "name" in lower or "naam" in lower:
            return {
                "intent": "recall_fact",
                "tool": "recall_fact",
                "arguments": {"key": "user_name"},
                "confidence": 0.98
            }
        return {
            "intent": "recall_fact",
            "tool": "recall_fact",
            "arguments": {"key": "all"},
            "confidence": 0.95
        }

    # 16. Web Search / Knowledge: "search latest AI news", "explain quantum computing", "latest news"
    if any(k in lower for k in ["search", "dhoondo", "batao", "explain", "who is", "what is", "kaun hai", "news"]):
        query = cleaned
        for p in ["search ", "dhoondo ", "tell me about ", "explain "]:
            if lower.startswith(p):
                query = cleaned[len(p):]
                break
        return {
            "intent": "search_web",
            "tool": "search_web",
            "arguments": {"query": query},
            "confidence": 0.85
        }

    # 17. Greetings / Conversational
    if any(k in lower for k in ["hello", "hi", "hey", "namaste", "kaise ho", "kya haal hai", "good morning", "good evening"]):
        return {
            "intent": "greeting",
            "tool": None,
            "arguments": {},
            "confidence": 0.99
        }

    # Default general query
    return {
        "intent": "general_query",
        "tool": "search_web",
        "arguments": {"query": cleaned},
        "confidence": 0.70
    }
