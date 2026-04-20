"""
IITIAN AI - Memory Manager
Handles short-term working context, long-term semantic key-value memory, and conversation history.
"""

import datetime
import json
from backend.memory.storage import storage

class MemoryManager:
    def __init__(self, db_storage=storage):
        self.storage = db_storage
        self.short_term_context = {
            "last_intent": None,
            "last_action": None,
            "last_target": None,
            "awaiting_confirmation": None,
            "session_start": datetime.datetime.now().isoformat()
        }

    # --- Long Term Memory (Key-Value & Facts) ---

    def set_memory(self, key: str, value: str, category: str = "general") -> dict:
        key = key.strip().lower().replace(" ", "_")
        now = datetime.datetime.now().isoformat()
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memory_kv (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    updated_at=excluded.updated_at
            """, (key, value.strip(), category, now))
            conn.commit()
        return {"key": key, "value": value, "category": category, "updated_at": now}

    def get_memory(self, key: str):
        key = key.strip().lower().replace(" ", "_")
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM memory_kv WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None

    def delete_memory(self, key: str) -> bool:
        key = key.strip().lower().replace(" ", "_")
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory_kv WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    def list_all_memories(self) -> list:
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, category, updated_at FROM memory_kv ORDER BY category, key")
            return [dict(row) for row in cursor.fetchall()]

    def search_memories(self, query: str) -> list:
        query_like = f"%{query.lower()}%"
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT key, value, category, updated_at FROM memory_kv
                WHERE LOWER(key) LIKE ? OR LOWER(value) LIKE ? OR LOWER(category) LIKE ?
            """, (query_like, query_like, query_like))
            return [dict(row) for row in cursor.fetchall()]

    # --- Conversation History & Context ---

    def add_conversation(self, role: str, message: str, intent: str = None, tool_calls: list = None):
        now = datetime.datetime.now().isoformat()
        tool_json = json.dumps(tool_calls) if tool_calls else None
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (timestamp, role, message, intent, tool_calls)
                VALUES (?, ?, ?, ?, ?)
            """, (now, role, message, intent, tool_json))
            conn.commit()

        # Update short term context
        if intent:
            self.short_term_context["last_intent"] = intent

    def get_recent_history(self, limit: int = 10) -> list:
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, role, message, intent, tool_calls
                FROM conversations
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            history = []
            for row in reversed(rows):
                d = dict(row)
                if d.get("tool_calls"):
                    try:
                        d["tool_calls"] = json.loads(d["tool_calls"])
                    except Exception:
                        pass
                history.append(d)
            return history

    def get_user_profile(self) -> dict:
        memories = self.list_all_memories()
        profile = {}
        for m in memories:
            profile[m["key"]] = m["value"]
        return profile

    def build_system_context(self) -> str:
        profile = self.get_user_profile()
        context_lines = [
            f"User Name: {profile.get('user_name', 'User')}",
            f"Assistant Name: {profile.get('assistant_name', 'IITIAN')}",
            f"Language Preference: {profile.get('preferred_language', 'Hinglish')}",
        ]
        other_facts = [f"{k}: {v}" for k, v in profile.items() if k not in ["user_name", "assistant_name", "preferred_language"]]
        if other_facts:
            context_lines.append("Known facts: " + "; ".join(other_facts))
        return "\n".join(context_lines)

    # --- Audit & Security Logs ---

    def log_audit(self, action: str, details: str, status: str = "success"):
        now = datetime.datetime.now().isoformat()
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, action, details, status)
                VALUES (?, ?, ?, ?)
            """, (now, action, details, status))
            conn.commit()

memory_manager = MemoryManager()
