"""
IITIAN AI - Database Storage Layer
SQLite persistent storage for alarms, reminders, contacts, calendar, memory, and logs.
"""

import sqlite3
import json
import uuid
import datetime
from pathlib import Path
from backend.config import DB_PATH, DEFAULT_USER_NAME

class Storage:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Key-Value Memory Store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_kv (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    updated_at TEXT NOT NULL
                )
            """)

            # Alarms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alarms (
                    id TEXT PRIMARY KEY,
                    time_str TEXT NOT NULL,
                    label TEXT DEFAULT 'Alarm',
                    repeat_days TEXT DEFAULT '',
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL
                )
            """)

            # Timers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS timers (
                    id TEXT PRIMARY KEY,
                    duration INTEGER NOT NULL,
                    label TEXT DEFAULT 'Timer',
                    ends_at REAL NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL
                )
            """)

            # Reminders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    remind_at TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL
                )
            """)

            # Calendar Events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    location TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # Contacts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    email TEXT,
                    relation TEXT,
                    notes TEXT
                )
            """)

            # Conversation History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    intent TEXT,
                    tool_calls TEXT
                )
            """)

            # Audit Logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    status TEXT DEFAULT 'success'
                )
            """)

            conn.commit()
            
            # Seed default contacts and memories if empty
            self._seed_defaults(cursor, conn)

    def _seed_defaults(self, cursor, conn):
        # Seed default memory
        cursor.execute("SELECT COUNT(*) as count FROM memory_kv")
        if cursor.fetchone()["count"] == 0:
            now = datetime.datetime.now().isoformat()
            defaults = [
                ("user_name", DEFAULT_USER_NAME, "profile", now),
                ("assistant_name", "IITIAN", "system", now),
                ("college", "IIT", "education", now),
                ("preferred_language", "Hinglish", "preference", now),
                ("favorite_topics", "Artificial Intelligence, Agentic Systems, Machine Learning", "interest", now),
            ]
            cursor.executemany("INSERT INTO memory_kv (key, value, category, updated_at) VALUES (?, ?, ?, ?)", defaults)

        # Seed default contacts
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        if cursor.fetchone()["count"] == 0:
            default_contacts = [
                (str(uuid.uuid4())[:8], "Papa", "+91 9876543210", "papa@family.com", "Father", "Always picks up call"),
                (str(uuid.uuid4())[:8], "Mom", "+91 9876543211", "mom@family.com", "Mother", "Family contact"),
                (str(uuid.uuid4())[:8], "Rahul", "+91 9876543212", "rahul@college.edu", "Friend", "College friend & project partner"),
                (str(uuid.uuid4())[:8], "Professor", "+91 9876543213", "professor@iit.ac.in", "Mentor", "Project advisor"),
            ]
            cursor.executemany("INSERT INTO contacts (id, name, phone, email, relation, notes) VALUES (?, ?, ?, ?, ?, ?)", default_contacts)

        # Seed sample upcoming event
        cursor.execute("SELECT COUNT(*) as count FROM calendar_events")
        if cursor.fetchone()["count"] == 0:
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 10:00")
            cursor.execute(
                "INSERT INTO calendar_events (id, title, start_time, end_time, location, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4())[:8], "AI Project Review Meeting", tomorrow, "", "Lab / Online", "Review IITIAN Voice Assistant features", datetime.datetime.now().isoformat())
            )

        # Seed sample reminder
        cursor.execute("SELECT COUNT(*) as count FROM reminders")
        if cursor.fetchone()["count"] == 0:
            tomorrow_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 10:00")
            cursor.execute(
                "INSERT INTO reminders (id, text, remind_at, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4())[:8], "Email professor regarding project review", tomorrow_time, "high", "pending", datetime.datetime.now().isoformat())
            )

        conn.commit()

# Global storage instance
storage = Storage()
