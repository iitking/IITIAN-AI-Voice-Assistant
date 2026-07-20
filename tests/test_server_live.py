"""
Test real-time HTTP server endpoints and agent interactions.
"""

import urllib.request
import json
import threading
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.server import run_server

def test_live_server():
    # Start server in thread
    t = threading.Thread(target=run_server, kwargs={"host": "127.0.0.1", "port": 8089}, daemon=True)
    t.start()
    time.sleep(1.0)

    base = "http://127.0.0.1:8089"

    # 1. Health
    with urllib.request.urlopen(f"{base}/api/health") as resp:
        data = json.loads(resp.read().decode())
        print("1. Health Check:", data)
        assert data["status"] == "online"

    # 2. State
    with urllib.request.urlopen(f"{base}/api/state") as resp:
        state = json.loads(resp.read().decode())
        print("2. System State (Alarms count):", len(state.get("alarms", [])))
        print("   System State (Contacts count):", len(state.get("contacts", [])))
        assert "battery" in state

    # 3. Chat: Single Command
    req = urllib.request.Request(
        f"{base}/api/chat",
        data=json.dumps({"message": "Kal subah 7 baje ka alarm laga do"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print("\n3. Chat Single Command Response:")
        print("   Spoken:", res["spoken_response"])
        print("   Tools:", [t["tool"] for t in res["executed_tools"]])
        assert any(t["tool"] == "set_alarm" for t in res["executed_tools"])

    # 4. Chat: Multi-Step Agentic Command
    req2 = urllib.request.Request(
        f"{base}/api/chat",
        data=json.dumps({"message": "Tomorrow wake me up at 7 AM, check the weather in Jaipur, and remind me to email my professor at 10 AM"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req2) as resp:
        res2 = json.loads(resp.read().decode())
        print("\n4. Chat Multi-Step Command Response:")
        print("   Spoken:", res2["spoken_response"])
        print("   Plan Steps:", res2["plan"]["total_steps"])
        print("   Tools Executed:", [t["tool"] for t in res2["executed_tools"]])
        assert res2["plan"]["is_multi_step"] is True

    # 5. Chat: Call Contact
    req3 = urllib.request.Request(
        f"{base}/api/chat",
        data=json.dumps({"message": "Papa ko call lagao"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req3) as resp:
        res3 = json.loads(resp.read().decode())
        print("\n5. Call Command Response:")
        print("   Spoken:", res3["spoken_response"])
        assert any(t["tool"] == "call_contact" for t in res3["executed_tools"])

    # 6. Static files
    with urllib.request.urlopen(f"{base}/") as resp:
        html = resp.read().decode()
        print("\n6. Static HTML Loaded, length:", len(html))
        assert "IITIAN" in html

    print("\n✅ All Live Server & Agent E2E Tests Passed Successfully!")

if __name__ == "__main__":
    test_live_server()
