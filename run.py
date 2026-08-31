"""
IITIAN AI - Master One-Click Runner
Starts the backend server and automatically opens the futuristic Voice UI in your browser.
"""

import sys
import time
import webbrowser
import threading
from backend.config import HOST, PORT
from backend.server import run_server

def open_browser():
    time.sleep(1.2)
    url = f"http://{HOST}:{PORT}"
    print(f"🚀 Opening IITIAN Assistant Web UI at {url}...")
    webbrowser.open(url)

if __name__ == "__main__":
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()
    run_server(HOST, PORT)
