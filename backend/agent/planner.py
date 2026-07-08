"""
IITIAN AI - Multi-Step Task Planner
Decomposes complex, multi-intent voice instructions into structured executable pipelines.
"""

import re
from backend.agent.intent import classify_intent

class TaskPlanner:
    def plan(self, user_prompt: str) -> dict:
        """
        Takes a raw user prompt, checks if it is a compound command,
        and generates an execution plan consisting of sequential sub-tasks.
        """
        # Strip wake words
        cleaned = self._strip_wake_words(user_prompt)
        
        # Check if the prompt has sub-clauses
        sub_clauses = self._split_clauses(cleaned)
        
        steps = []
        step_num = 1

        for clause in sub_clauses:
            clause = clause.strip()
            if not clause:
                continue
            
            # Check for conditional triggers (e.g. "if it rains remind me to carry umbrella")
            condition = None
            if "if it rain" in clause.lower() or "agar barish" in clause.lower():
                condition = "weather_rain"

            classification = classify_intent(clause)
            
            steps.append({
                "step": step_num,
                "sub_goal": clause,
                "intent": classification["intent"],
                "tool": classification["tool"],
                "arguments": classification["arguments"],
                "condition": condition
            })
            step_num += 1

        # If no steps extracted, create a single fallback step
        if not steps:
            classification = classify_intent(cleaned)
            steps.append({
                "step": 1,
                "sub_goal": cleaned,
                "intent": classification["intent"],
                "tool": classification["tool"],
                "arguments": classification["arguments"],
                "condition": None
            })

        return {
            "prompt": user_prompt,
            "cleaned_prompt": cleaned,
            "is_multi_step": len(steps) > 1,
            "total_steps": len(steps),
            "steps": steps
        }

    def _strip_wake_words(self, text: str) -> str:
        lower = text.lower()
        wake_patterns = [
            r'^(?:hey|hello|hi|namaste|ok|sun)?\s*iitian[,:]?\s*',
            r'^(?:hey|hello|hi)?\s*assistant[,:]?\s*',
        ]
        res = text
        for pat in wake_patterns:
            res = re.sub(pat, '', res, flags=re.IGNORECASE)
        return res.strip()

    def _split_clauses(self, text: str) -> list:
        """
        Splits multi-action commands joined by 'and', 'aur', 'also', 'phir', 'fir', commas or semicolons.
        Careful not to split inside times or numbers.
        """
        # Split on commas, semicolons, and compound conjunctions
        pattern = r'(?:\s+and\s+also\s+|\s+and\s+|\s+aur\s+bhi\s+|\s+aur\s+|\s+also\s+|\s+phir\s+|\s+fir\s+|,\s*|\.\s+)'
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        # Merge parts if too short
        merged = []
        buffer = ""
        for p in parts:
            p = p.strip()
            if not p:
                continue
            if len(p.split()) <= 1 and buffer:
                buffer += " " + p
            else:
                if buffer:
                    merged.append(buffer)
                buffer = p
        if buffer:
            merged.append(buffer)
            
        return merged if len(merged) > 1 else [text]

task_planner = TaskPlanner()
