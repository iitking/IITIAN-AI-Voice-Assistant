"""
IITIAN AI - Interactive Terminal CLI Assistant
Listen. Understand. Remember. Think. Plan. Execute.
Created by Nivesh Kumar Meena
"""

import sys
import os
import time
from backend.agent.orchestrator import orchestrator
from backend.speech.tts_engine import speak
from backend.config import ASSISTANT_NAME

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    banner = f"""
{CYAN}{BOLD}======================================================================
       🤖 {ASSISTANT_NAME} — YOUR PERSONAL REAL-TIME AI VOICE ASSISTANT
======================================================================{RESET}
  {MAGENTA}Listen. Understand. Remember. Think. Plan. Execute.{RESET}
  Created with ❤️  by {YELLOW}Nivesh Kumar Meena{RESET}

  {GREEN}Supported Commands Examples:{RESET}
  • "Kal subah 7 baje ka alarm laga do"
  • "Papa ko call lagao"
  • "Papa ko message karo ki main 8 baje ghar aaunga"
  • "Kal 10 baje professor ko email yaad dilana"
  • "Jaipur me mausam kaisa hai?"
  • "Calculate 250 * 48" or "Convert 10 km to miles"
  • "Open Chrome" / "Open VS Code"
  • "Battery kitni hai?" / "Volume 50 percent karo"
  • "My name is Nivesh" -> "What is my name?"
  • Multi-step: "Set alarm for 7 AM, check weather in Jaipur, and remind me to study at 8 PM"
  • Type {YELLOW}'voice'{RESET} to toggle speech output, or {YELLOW}'exit'{RESET} to quit.
{CYAN}----------------------------------------------------------------------{RESET}
"""
    print(banner)

def main():
    print_banner()
    voice_enabled = True

    while True:
        try:
            prompt_str = f"{BOLD}{CYAN}You 🎤 >> {RESET}"
            user_input = input(prompt_str).strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                farewell = "Goodbye Nivesh! Have a great day ahead."
                print(f"\n{BOLD}{MAGENTA}{ASSISTANT_NAME}:{RESET} {farewell}\n")
                if voice_enabled:
                    speak(farewell)
                time.sleep(1)
                break

            if user_input.lower() == "voice":
                voice_enabled = not voice_enabled
                state_str = "ON" if voice_enabled else "OFF"
                print(f"{YELLOW}Voice playback toggled {state_str}.{RESET}\n")
                continue

            print(f"{BLUE}Thinking & Planning...{RESET}")
            response = orchestrator.process(user_input, mode="cli")

            # Show Plan if multi-step
            plan = response.get("plan", {})
            if plan and plan.get("is_multi_step"):
                print(f"\n{YELLOW}[Agent Plan Breakdown - {plan['total_steps']} steps]{RESET}")
                for s in plan["steps"]:
                    print(f"  Step {s['step']}: {s['sub_goal']} -> Tool: {s['tool']}")

            # Show Executed Tools
            executed = response.get("executed_tools", [])
            if executed:
                print(f"\n{GREEN}[Tools Executed]{RESET}")
                for e in executed:
                    print(f"  ✓ {e['tool']} with args {e['arguments']}")

            spoken = response.get("spoken_response", "")
            print(f"\n{BOLD}{MAGENTA}{ASSISTANT_NAME} 🔊:{RESET} {spoken}\n")

            if voice_enabled and spoken:
                speak(spoken)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting IITIAN Assistant...")
            break

if __name__ == "__main__":
    main()
