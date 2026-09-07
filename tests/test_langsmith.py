"""
IITIAN AI - LangSmith Observability Test Suite
Tests trace creation, status reporting, and orchestrator trace attachment.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.monitoring.langsmith_tracer import tracer, get_recent_traces
from backend.agent.orchestrator import orchestrator

class TestLangSmithTracing(unittest.TestCase):

    def test_01_tracer_status(self):
        status = tracer.get_status()
        self.assertIn("enabled", status)
        self.assertIn("project", status)
        self.assertIn("mode", status)
        self.assertEqual(status["project"], tracer.project)

    def test_02_trace_agent_execution(self):
        run_id = tracer.trace_agent_execution(
            user_prompt="Kal subah 7 baje ka alarm laga do",
            plan={"total_steps": 1, "is_multi_step": False},
            executed_tools=[{"tool": "set_alarm"}],
            spoken_response="Alarm set for 7 AM",
            latency_ms=45.2
        )
        self.assertIsNotNone(run_id)
        self.assertTrue(len(run_id) > 10)

        # Check local trace buffer
        recent = get_recent_traces(5)
        self.assertTrue(any(t["name"] == "IITIAN_Agent_Orchestrator" for t in recent))

    def test_03_trace_tool_execution(self):
        run_id = tracer.trace_tool_execution(
            tool_name="get_weather",
            arguments={"city": "Jaipur"},
            result={"temperature": "31°C", "condition": "Sunny"},
            latency_ms=12.5
        )
        self.assertIsNotNone(run_id)
        recent = get_recent_traces(5)
        self.assertTrue(any("Tool:get_weather" in t["name"] for t in recent))

    def test_04_orchestrator_live_trace(self):
        res = orchestrator.process("Calculate 50 * 20", mode="test")
        self.assertIn("trace_id", res)
        self.assertIsNotNone(res["trace_id"])
        recent = get_recent_traces(5)
        self.assertTrue(any(t["id"] == res["trace_id"] for t in recent))

if __name__ == "__main__":
    unittest.main()
