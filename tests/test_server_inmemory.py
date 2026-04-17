"""
IITIAN AI - In-Memory Server & Handler Test Suite
Tests HTTP request processing, endpoints, headers, JSON encoding without opening network sockets.
"""

import sys
import json
import unittest
from io import BytesIO
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.server import IITIANRequestHandler

class DummyServer:
    pass

class MockSocket:
    def __init__(self, data=b""):
        self.rfile = BytesIO(data)
        self.wfile = BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if 'r' in mode:
            return self.rfile
        elif 'w' in mode:
            return self.wfile

class TestIITIANServerInMemory(unittest.TestCase):

    def _call_handler(self, method, path, body=None):
        raw_body = json.dumps(body).encode() if body else b""
        mock_sock = MockSocket(raw_body)

        # Initialize handler without real network socket
        handler = IITIANRequestHandler.__new__(IITIANRequestHandler)
        handler.rfile = mock_sock.rfile
        handler.wfile = mock_sock.wfile
        handler.headers = {"Content-Length": str(len(raw_body)), "Content-Type": "application/json"}
        handler.path = path
        handler.command = method
        handler.request_version = "HTTP/1.1"
        handler.requestline = f"{method} {path} HTTP/1.1"

        if method == "GET":
            handler.do_GET()
        elif method == "POST":
            handler.do_POST()

        mock_sock.wfile.seek(0)
        output = mock_sock.wfile.read()
        return output

    def test_health_endpoint(self):
        output = self._call_handler("GET", "/api/health")
        self.assertIn(b"200 OK", output)
        self.assertIn(b"IITIAN", output)
        self.assertIn(b"online", output)

    def test_state_endpoint(self):
        output = self._call_handler("GET", "/api/state")
        self.assertIn(b"200 OK", output)
        self.assertIn(b"alarms", output)
        self.assertIn(b"contacts", output)
        self.assertIn(b"battery", output)

    def test_chat_endpoint_alarm(self):
        output = self._call_handler("POST", "/api/chat", {"message": "Kal subah 7 baje ka alarm laga do"})
        self.assertIn(b"200 OK", output)
        self.assertIn(b"set_alarm", output)

    def test_chat_endpoint_multistep(self):
        output = self._call_handler("POST", "/api/chat", {
            "message": "Tomorrow wake me up at 7 AM, check the weather in Jaipur, and remind me to email my professor at 10 AM"
        })
        self.assertIn(b"200 OK", output)
        self.assertIn(b"total_steps", output)
        self.assertIn(b"spoken_response", output)

    def test_static_html_endpoint(self):
        output = self._call_handler("GET", "/")
        self.assertIn(b"200 OK", output)
        self.assertIn(b"<!DOCTYPE html>", output)
        self.assertIn(b"IITIAN", output)

if __name__ == "__main__":
    unittest.main()
