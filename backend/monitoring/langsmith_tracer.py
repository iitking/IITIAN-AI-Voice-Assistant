"""
IITIAN AI - LangSmith Observability & Tracing Module
Seamlessly integrates with LangSmith to trace agent workflows, task planning, and tool calls.
Supports official LangSmith SDK and zero-dependency direct HTTP ingestion fallback.
"""

import os
import sys
import time
import json
import uuid
import threading
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from backend.config import (
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
    LANGCHAIN_ENDPOINT,
    DATA_DIR
)
from backend.memory.storage import storage

# In-memory recent trace ring buffer
_RECENT_TRACES = []
_MAX_LOCAL_TRACES = 50

# Check if official langsmith SDK is installed
_SDK_AVAILABLE = False
try:
    import langsmith
    from langsmith import Client, RunTree
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


class LangSmithTracer:
    def __init__(self):
        self.enabled = LANGCHAIN_TRACING_V2 or bool(LANGCHAIN_API_KEY)
        self.api_key = LANGCHAIN_API_KEY or os.getenv("LANGCHAIN_API_KEY", "")
        self.project = LANGCHAIN_PROJECT or os.getenv("LANGCHAIN_PROJECT", "IITIAN-Voice-Assistant")
        self.endpoint = (LANGCHAIN_ENDPOINT or "https://api.smith.langchain.com").rstrip("/")
        self.sdk_client = None

        if self.enabled and self.api_key and _SDK_AVAILABLE:
            try:
                self.sdk_client = Client(api_key=self.api_key, api_url=self.endpoint)
            except Exception as e:
                sys.stderr.write(f"[LangSmith] SDK client init warning: {e}\n")

    def get_status(self) -> dict:
        """Returns the current observability status."""
        has_key = bool(self.api_key)
        masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if (has_key and len(self.api_key) > 12) else ("Configured" if has_key else "Missing")
        mode = "sdk" if (self.sdk_client and _SDK_AVAILABLE) else ("direct_api" if (has_key and self.enabled) else "local_buffer")
        
        return {
            "enabled": self.enabled and has_key,
            "has_api_key": has_key,
            "masked_key": masked_key,
            "project": self.project,
            "endpoint": self.endpoint,
            "sdk_installed": _SDK_AVAILABLE,
            "mode": mode,
            "total_local_traces": len(_RECENT_TRACES),
            "cloud_url": f"https://smith.langchain.com/o/default/projects/p/{self.project}" if has_key else "https://smith.langchain.com/"
        }

    def trace_agent_execution(self, user_prompt: str, plan: dict, executed_tools: list, spoken_response: str, latency_ms: float, status: str = "success") -> str:
        """
        Traces a top-level user voice/text interaction through the Agent Orchestrator.
        """
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        run_payload = {
            "id": run_id,
            "name": "IITIAN_Agent_Orchestrator",
            "run_type": "chain",
            "inputs": {"user_prompt": user_prompt},
            "outputs": {
                "spoken_response": spoken_response,
                "executed_tools_count": len(executed_tools),
                "is_multi_step": plan.get("is_multi_step", False) if plan else False
            },
            "extra": {
                "metadata": {
                    "assistant": "IITIAN",
                    "plan_steps": plan.get("total_steps", 1) if plan else 1,
                    "tools": [t.get("tool") for t in executed_tools],
                    "status": status,
                    "latency_ms": round(latency_ms, 2)
                }
            },
            "start_time": now,
            "end_time": now,
            "session_name": self.project
        }

        # Store in local ring buffer
        _add_local_trace(run_payload)

        # Dispatch to LangSmith Cloud
        self._dispatch_to_cloud(run_payload)
        return run_id

    def trace_tool_execution(self, tool_name: str, arguments: dict, result: dict, latency_ms: float, parent_run_id: str = None) -> str:
        """
        Traces an individual tool execution within the Agent pipeline.
        """
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        run_payload = {
            "id": run_id,
            "parent_run_id": parent_run_id,
            "name": f"Tool:{tool_name}",
            "run_type": "tool",
            "inputs": arguments or {},
            "outputs": result or {},
            "extra": {
                "metadata": {
                    "tool": tool_name,
                    "success": result.get("success", False) if isinstance(result, dict) else True,
                    "latency_ms": round(latency_ms, 2)
                }
            },
            "start_time": now,
            "end_time": now,
            "session_name": self.project
        }

        _add_local_trace(run_payload)
        self._dispatch_to_cloud(run_payload)
        return run_id

    def trace_planner(self, raw_prompt: str, plan_result: dict, latency_ms: float) -> str:
        """
        Traces task decomposition performed by the Task Planner.
        """
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        run_payload = {
            "id": run_id,
            "name": "IITIAN_Task_Planner",
            "run_type": "chain",
            "inputs": {"raw_prompt": raw_prompt},
            "outputs": {
                "is_multi_step": plan_result.get("is_multi_step", False),
                "total_steps": plan_result.get("total_steps", 0),
                "steps": [s.get("sub_goal") for s in plan_result.get("steps", [])]
            },
            "extra": {
                "metadata": {
                    "latency_ms": round(latency_ms, 2)
                }
            },
            "start_time": now,
            "end_time": now,
            "session_name": self.project
        }

        _add_local_trace(run_payload)
        self._dispatch_to_cloud(run_payload)
        return run_id

    def _dispatch_to_cloud(self, run_payload: dict):
        """Dispatches run to LangSmith asynchronously in a background thread."""
        if not self.enabled or not self.api_key:
            return

        def _send():
            # If official SDK client available
            if self.sdk_client and _SDK_AVAILABLE:
                try:
                    self.sdk_client.create_run(
                        name=run_payload["name"],
                        run_type=run_payload["run_type"],
                        inputs=run_payload["inputs"],
                        outputs=run_payload["outputs"],
                        extra=run_payload["extra"],
                        project_name=self.project
                    )
                    return
                except Exception:
                    pass

            # Direct HTTP API fallback (works without SDK!)
            try:
                url = f"{self.endpoint}/runs"
                body = json.dumps(run_payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers={
                        "x-api-key": self.api_key,
                        "Content-Type": "application/json",
                        "User-Agent": "IITIAN-Voice-Assistant/1.0"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201, 202):
                        sys.stdout.write(f"[LangSmith] Trace '{run_payload.get('name')}' uploaded to '{self.project}' (HTTP {resp.status})\n")
                        sys.stdout.flush()
            except Exception:
                # Silently ignore network failures to never block voice assistant
                pass

        t = threading.Thread(target=_send, daemon=True)
        t.start()


def _add_local_trace(run_payload: dict):
    """Stores trace in in-memory ring buffer and SQLite audit table."""
    trace_summary = {
        "id": run_payload.get("id"),
        "name": run_payload.get("name"),
        "run_type": run_payload.get("run_type"),
        "inputs": run_payload.get("inputs"),
        "outputs": run_payload.get("outputs"),
        "latency_ms": run_payload.get("extra", {}).get("metadata", {}).get("latency_ms", 0),
        "timestamp": run_payload.get("start_time", datetime.now().isoformat())
    }
    _RECENT_TRACES.insert(0, trace_summary)
    if len(_RECENT_TRACES) > _MAX_LOCAL_TRACES:
        _RECENT_TRACES.pop()


def get_recent_traces(limit: int = 20) -> list:
    """Returns recently recorded traces."""
    return _RECENT_TRACES[:limit]


# Global singleton tracer
tracer = LangSmithTracer()
