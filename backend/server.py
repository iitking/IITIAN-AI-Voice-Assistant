"""
IITIAN AI - Real-Time Server
Zero-dependency, multi-threaded HTTP and SSE API server for IITIAN Voice Assistant.
"""

import sys
import json
import time
import mimetypes
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

from backend.config import HOST, PORT, FRONTEND_DIR, DATA_DIR, ASSISTANT_NAME
from backend.agent.orchestrator import orchestrator
from backend.tools.alarm import list_alarms, list_timers, delete_alarm, stop_timer, dismiss_timer
from backend.tools.reminders import get_reminders, complete_reminder, delete_reminder
from backend.tools.calendar import get_upcoming_events, delete_event
from backend.tools.calling import list_contacts, add_contact
from backend.tools.computer import get_battery_status
from backend.tools.registry import execute_tool, get_tools_manifest
from backend.memory.memory_manager import memory_manager
from backend.speech.tts_engine import speak
from backend.monitoring.langsmith_tracer import tracer, get_recent_traces

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class IITIANRequestHandler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            self.close_connection = True

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[{time.strftime('%X')}] {args[0]} - {args[1]}\n")

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        path = self.path.split("?")[0]

        # 1. Health check
        if path == "/api/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "online",
                "assistant": ASSISTANT_NAME,
                "version": "1.0.0"
            }).encode())
            return

        # Monitoring status
        if path == "/api/monitoring/status":
            self._set_headers(200)
            self.wfile.write(json.dumps(tracer.get_status()).encode())
            return

        # Monitoring traces
        if path == "/api/monitoring/traces":
            self._set_headers(200)
            self.wfile.write(json.dumps({"traces": get_recent_traces(30)}).encode())
            return

        # 2. Get full system state (alarms, timers, reminders, calendar, contacts, battery, monitoring)
        if path == "/api/state":
            self._set_headers(200)
            state = {
                "alarms": list_alarms(),
                "timers": list_timers(),
                "reminders": get_reminders(),
                "events": get_upcoming_events(),
                "contacts": list_contacts(),
                "memories": memory_manager.list_all_memories(),
                "battery": get_battery_status(),
                "history": memory_manager.get_recent_history( limit=10 ),
                "tools": get_tools_manifest(),
                "user_profile": memory_manager.get_user_profile(),
                "monitoring": tracer.get_status(),
                "recent_traces": get_recent_traces(10)
            }
            self.wfile.write(json.dumps(state).encode())
            return

        # 3. Server-Sent Events (SSE) Stream
        if path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            try:
                alerted_timer_ids = set()
                while not self.close_connection:
                    # Check timers
                    timers = list_timers()
                    finished_timers = []
                    for t in timers:
                        if t.get("is_finished") and t["id"] not in alerted_timer_ids:
                            finished_timers.append(t)
                            alerted_timer_ids.add(t["id"])

                    event_payload = {
                        "timestamp": time.time(),
                        "timers": timers,
                        "finished_timers": finished_timers
                    }
                    data_str = f"data: {json.dumps(event_payload)}\n\n"
                    self.wfile.write(data_str.encode())
                    self.wfile.flush()
                    time.sleep(1)
            except Exception:
                self.close_connection = True
                return

        # 4. Static Frontend Assets
        self._serve_static(path)

    def do_POST(self):
        path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Main Chat / Voice Input Endpoint
        if path == "/api/chat":
            message = payload.get("message", "")
            mode = payload.get("mode", "voice")
            should_speak = payload.get("speak", False)

            response = orchestrator.process(message, mode=mode)

            # Optional backend native macOS voice output
            if should_speak and response.get("spoken_response"):
                speak(response["spoken_response"])

            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode())
            return

        # 2. Direct Actions (alarm dismissal, reminder toggle, etc.)
        if path == "/api/action":
            action = payload.get("action")
            res = {"success": False, "message": "Unknown action"}

            if action == "delete_alarm":
                res = delete_alarm(payload.get("id"))
            elif action == "stop_timer":
                res = stop_timer(payload.get("id"))
            elif action == "dismiss_timer":
                res = dismiss_timer(payload.get("id", ""))
            elif action == "complete_reminder":
                res = complete_reminder(payload.get("id"))
            elif action == "delete_reminder":
                res = delete_reminder(payload.get("id"))
            elif action == "delete_event":
                res = delete_event(payload.get("id"))
            elif action == "save_memory":
                res = memory_manager.set_memory(payload.get("key", ""), payload.get("value", ""), payload.get("category", "general"))
            elif action == "delete_memory":
                res = {"success": memory_manager.delete_memory(payload.get("key", ""))}
            elif action == "add_contact":
                res = add_contact(payload.get("name", ""), payload.get("phone", ""), payload.get("relation", ""), payload.get("email", ""))
            elif action == "execute_tool":
                res = execute_tool(payload.get("tool"), payload.get("args", {}))
            elif action == "save_langsmith_key":
                key = payload.get("key", "").strip()
                project = payload.get("project", "IITIAN-Voice-Assistant").strip()
                if key:
                    from backend.config import BASE_DIR
                    content = f"LANGCHAIN_TRACING_V2=true\nLANGCHAIN_API_KEY={key}\nLANGCHAIN_PROJECT={project}\nLANGCHAIN_ENDPOINT=https://api.smith.langchain.com\n"
                    try:
                        with open(BASE_DIR / "config.env", "w", encoding="utf-8") as f:
                            f.write(content)
                        with open(BASE_DIR / ".env", "w", encoding="utf-8") as f:
                            f.write(content)
                        os.environ["LANGCHAIN_TRACING_V2"] = "true"
                        os.environ["LANGCHAIN_API_KEY"] = key
                        os.environ["LANGCHAIN_PROJECT"] = project
                        tracer.api_key = key
                        tracer.enabled = True
                        tracer.project = project
                        res = {"success": True, "message": "LangSmith API key saved successfully!"}
                    except Exception as e:
                        res = {"success": False, "message": str(e)}
                else:
                    res = {"success": False, "message": "API key cannot be empty."}

            self._set_headers(200)
            self.wfile.write(json.dumps(res).encode())
            return

        # 3. Direct TTS trigger endpoint
        if path == "/api/tts":
            text = payload.get("text", "")
            if text:
                speak(text)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True}).encode())
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def _serve_static(self, path):
        if path == "/" or path == "":
            file_path = FRONTEND_DIR / "index.html"
        else:
            rel_path = path.lstrip("/")
            file_path = FRONTEND_DIR / rel_path

        if file_path.exists() and file_path.is_file():
            mime_type, _ = mimetypes.guess_type(str(file_path))
            content_type = mime_type or "text/plain"
            self._set_headers(200, content_type=content_type)
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._set_headers(404, content_type="text/html")
            self.wfile.write(b"<h1>404 - Not Found</h1>")

def run_server(host=HOST, port=PORT):
    server = ThreadedHTTPServer((host, port), IITIANRequestHandler)
    print(f"==================================================")
    print(f"🤖 IITIAN AI Assistant Server Running")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"⚡ Real-Time Voice Engine Ready")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping IITIAN Server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
