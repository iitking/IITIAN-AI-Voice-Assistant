"""
IITIAN AI - Central Agent Orchestrator
Coordinates reasoning, planning, multi-step execution, and conversational response generation.
"""

import json
import os
import time
import urllib.request
import urllib.parse
from backend.config import ASSISTANT_NAME, DEFAULT_USER_NAME, LLM_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY, OLLAMA_HOST, OLLAMA_MODEL
from backend.agent.planner import task_planner
from backend.tools.registry import execute_tool, TOOLS
from backend.memory.memory_manager import memory_manager
from backend.monitoring.langsmith_tracer import tracer

class AgentOrchestrator:
    def __init__(self):
        self.planner = task_planner
        self.memory = memory_manager

    def process(self, user_input: str, mode: str = "voice") -> dict:
        """
        Main entry point for user prompt.
        Decomposes into multi-step plan, executes tools, updates memory, and synthesizes response.
        """
        start_t = time.time()
        user_input_clean = user_input.strip()
        if not user_input_clean:
            return {
                "spoken_response": "I didn't hear anything. How can I help you?",
                "display_text": "I didn't catch that. Please speak or type your request.",
                "executed_tools": [],
                "plan": None
            }

        # Step 1: Generate Execution Plan
        plan = self.planner.plan(user_input_clean)
        
        executed_tools = []
        action_summaries = []
        last_weather_result = None

        # Step 2: Execute Plan Steps
        for step in plan["steps"]:
            intent = step["intent"]
            tool_name = step["tool"]
            arguments = step["arguments"]
            condition = step.get("condition")

            # Check conditional logic
            if condition == "weather_rain":
                # Only execute if previous weather result had rain
                if last_weather_result and not last_weather_result.get("umbrella_needed", False):
                    action_summaries.append("No rain forecast, skipping umbrella reminder.")
                    continue

            # Special case: Greeting
            if intent == "greeting":
                user_name = self.memory.get_memory("user_name") or DEFAULT_USER_NAME
                action_summaries.append(f"Namaste {user_name}! How can I help you today?")
                continue

            # Special case: Assistant Identity & Capabilities
            if intent == "assistant_info":
                from backend.config import ASSISTANT_CREATOR
                sub_type = arguments.get("type", "capabilities")
                if sub_type == "creator":
                    action_summaries.append(f"Mujhe {ASSISTANT_CREATOR} ne banaya hai ek powerful, real-time universal agentic AI assistant ke roop mein.")
                elif sub_type == "identity":
                    action_summaries.append(f"Main {ASSISTANT_NAME} hoon — aapka universal real-time voice & task assistant!")
                else:
                    action_summaries.append(f"Main {ASSISTANT_NAME} hoon. Main real-time alarms, countdown timers, live date aur time, math calculations, weather forecast, reminders, calendar meetings, Mac apps launch, aur system volume control kar sakta hoon.")
                continue

            # Special case: Recall memory
            if intent == "recall_fact":
                key = arguments.get("key", "user_name")
                if key == "all":
                    profile = self.memory.get_user_profile()
                    summary_facts = ", ".join([f"{k}: {v}" for k, v in profile.items()])
                    action_summaries.append(f"Here is what I remember: {summary_facts}")
                else:
                    val = self.memory.get_memory(key)
                    if val:
                        action_summaries.append(f"Your {key.replace('_', ' ')} is {val}.")
                    else:
                        action_summaries.append(f"I don't have information saved for '{key}' yet.")
                continue

            # Execute tool if present
            if tool_name and tool_name in TOOLS:
                exec_res = execute_tool(tool_name, arguments)
                executed_tools.append({
                    "step": step["step"],
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": exec_res
                })

                if exec_res.get("success"):
                    res_data = exec_res.get("result", {})
                    if tool_name == "get_weather":
                        last_weather_result = res_data

                    # Extract conversational voice message from tool output
                    summary = self._extract_summary(tool_name, res_data)
                    action_summaries.append(summary)
                else:
                    action_summaries.append(f"Could not complete {tool_name}: {exec_res.get('error', 'Unknown issue')}")
            else:
                # Direct response for general query
                if intent == "general_query":
                    search_res = execute_tool("search_web", {"query": user_input_clean})
                    if search_res.get("success"):
                        action_summaries.append(search_res["result"].get("summary", ""))

        # Step 3: Synthesize Final Conversational Output
        spoken_response = self._synthesize_voice_response(action_summaries, plan)
        display_text = self._build_display_text(action_summaries, executed_tools, plan)

        # Step 4: Record in Memory
        primary_intent = plan["steps"][0]["intent"] if plan["steps"] else "unknown"
        self.memory.add_conversation("user", user_input_clean, intent=primary_intent)
        self.memory.add_conversation("assistant", spoken_response, intent=primary_intent, tool_calls=executed_tools)

        # Step 5: LangSmith Observability Trace
        latency_ms = (time.time() - start_t) * 1000
        run_id = tracer.trace_agent_execution(
            user_prompt=user_input_clean,
            plan=plan,
            executed_tools=executed_tools,
            spoken_response=spoken_response,
            latency_ms=latency_ms
        )

        return {
            "spoken_response": spoken_response,
            "display_text": display_text,
            "executed_tools": executed_tools,
            "plan": plan,
            "trace_id": run_id,
            "user_profile": self.memory.get_user_profile()
        }

    def _extract_summary(self, tool_name: str, res_data: dict) -> str:
        if isinstance(res_data, dict):
            if "voice_response" in res_data:
                return res_data["voice_response"]
            if "message" in res_data:
                return res_data["message"]
            if "report" in res_data:
                return res_data["report"]
            if "summary" in res_data:
                return res_data["summary"]
            if "result" in res_data:
                return f"Result is {res_data['result']}."
        return "Action completed successfully."

    def _synthesize_voice_response(self, summaries: list, plan: dict) -> str:
        if not summaries:
            return "Task completed."
        
        if len(summaries) == 1:
            return summaries[0]
        
        # Multi-step synthesis
        combined = "All done! " + " Also, ".join(summaries)
        return combined

    def _build_display_text(self, summaries: list, executed_tools: list, plan: dict) -> str:
        lines = []
        for s in summaries:
            lines.append(f"- {s}")
        
        if executed_tools:
            lines.append("\n**Tools Executed:**")
            for t in executed_tools:
                lines.append(f"✓ `{t['tool']}`")
        return "\n".join(lines)

orchestrator = AgentOrchestrator()
