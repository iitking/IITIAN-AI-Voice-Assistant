"""
IITIAN AI - Configuration Module
Created for Nivesh Kumar Meena
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "iitian.db"
FRONTEND_DIR = BASE_DIR / "frontend"

# Assistant Identity
ASSISTANT_NAME = "IITIAN"
ASSISTANT_CREATOR = "Nivesh Kumar Meena"
DEFAULT_USER_NAME = "Nivesh"
DEFAULT_LANGUAGE = "Hinglish"  # English, Hindi, Hinglish

# Wake Words (lowercase)
WAKE_WORDS = [
    "hey iitian",
    "iitian",
    "hey assistant",
    "namaste iitian",
    "sun iitian",
    "hello iitian",
    "ok iitian",
]

# Auto-load .env or config.env file if present
def load_dotenv_file():
    candidates = [BASE_DIR / ".env", BASE_DIR / "config.env"]
    for env_file in candidates:
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

load_dotenv_file()

# Server Settings
HOST = os.getenv("IITIAN_HOST", "127.0.0.1")
PORT = int(os.getenv("IITIAN_PORT", 8080))

# LLM & AI Settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")  # local, openai, gemini, ollama
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# LangSmith Tracing & Observability
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() in ("true", "1", "yes")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "IITIAN-Voice-Assistant")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# Security & Risk Configuration
RISK_LEVELS = {
    "LOW": ["get_weather", "calculate", "search_web", "get_battery_status", "recall_memory", "get_reminders", "list_alarms"],
    "MEDIUM": ["set_alarm", "set_timer", "add_reminder", "add_calendar_event", "remember_memory", "open_application", "set_volume", "take_screenshot"],
    "HIGH": ["delete_alarm", "delete_file", "send_message", "call_contact"]
}

