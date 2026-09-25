"""
IITIAN AI - Comprehensive Automated Test Suite
Validates memory, tools, intent classification, task planner, and agent orchestrator.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.memory.memory_manager import memory_manager
from backend.tools.alarm import set_alarm, list_alarms, delete_alarm, set_timer, list_timers
from backend.tools.calling import get_contact, list_contacts, call_contact
from backend.tools.messaging import send_message
from backend.tools.calendar import add_event, get_upcoming_events
from backend.tools.reminders import add_reminder, get_reminders, complete_reminder
from backend.tools.weather import get_weather
from backend.tools.calculator import calculate
from backend.tools.computer import get_battery_status
from backend.tools.registry import execute_tool
from backend.agent.intent import classify_intent
from backend.agent.planner import task_planner
from backend.agent.orchestrator import orchestrator

class TestIITIANVoiceAssistant(unittest.TestCase):

    def test_01_memory_manager(self):
        # Test long term fact storage
        memory_manager.set_memory("favorite_subject", "Artificial Intelligence", "education")
        val = memory_manager.get_memory("favorite_subject")
        self.assertEqual(val, "Artificial Intelligence")

        # Test user profile retrieval
        profile = memory_manager.get_user_profile()
        self.assertIn("favorite_subject", profile)

    def test_02_alarm_and_timer_tools(self):
        # Set alarm
        alarm_res = set_alarm("06:30", "Morning Workout")
        self.assertTrue(alarm_res["success"])
        alarm_id = alarm_res["alarm_id"]

        alarms = list_alarms()
        self.assertTrue(any(a["id"] == alarm_id for a in alarms))

        # Set timer
        timer_res = set_timer(60, "Tea Timer")
        self.assertTrue(timer_res["success"])
        timers = list_timers()
        self.assertTrue(len(timers) > 0)

        # Cancel alarm
        del_res = delete_alarm(alarm_id)
        self.assertTrue(del_res["success"])

    def test_03_contacts_and_calling(self):
        # Preseeded Papa contact
        contact = get_contact("Papa")
        self.assertIsNotNone(contact)
        self.assertIn("+91", contact["phone"])

        # Call Papa
        call_res = call_contact("Papa")
        self.assertTrue(call_res["success"])
        self.assertEqual(call_res["contact_name"], "Papa")
        self.assertIn("tel:", call_res["tel_url"])

    def test_04_messaging(self):
        # Send WhatsApp message
        msg_res = send_message("Papa", "Main 8 baje ghar aaunga")
        self.assertTrue(msg_res["success"])
        self.assertIn("wa.me", msg_res["whatsapp_url"])
        self.assertIn("Main%208%20baje%20ghar%20aaunga", msg_res["whatsapp_url"])

    def test_05_reminders_and_calendar(self):
        # Add reminder
        rem_res = add_reminder("Review IITIAN code", "tomorrow 10:00", "high")
        self.assertTrue(rem_res["success"])
        
        # Complete reminder
        comp_res = complete_reminder(rem_res["reminder_id"])
        self.assertTrue(comp_res["success"])

        # Add calendar event
        ev_res = add_event("Project Demo", "tomorrow 11:00", location="Campus Lab")
        self.assertTrue(ev_res["success"])
        events = get_upcoming_events()
        self.assertTrue(len(events) > 0)

    def test_06_weather_and_calculator(self):
        # Weather
        w_res = get_weather("Jaipur")
        self.assertTrue(w_res["success"])
        self.assertIn("Jaipur", w_res["city"])
        self.assertIn("°C", w_res["temperature"])

        # Calculator math
        c1 = calculate("250 * 48")
        self.assertTrue(c1["success"])
        self.assertEqual(c1["result"], "12000")

        # Calculator percentage
        c2 = calculate("15% of 1200")
        self.assertTrue(c2["success"])
        self.assertEqual(c2["result"], "180.0")

        # Unit conversion
        c3 = calculate("10 km to miles")
        self.assertTrue(c3["success"])
        self.assertIn("6.21", c3["result"])

    def test_07_system_computer(self):
        # Battery check
        batt = get_battery_status()
        self.assertTrue(batt["success"])

    def test_08_intent_classification(self):
        # Alarm intent
        c1 = classify_intent("kal subah 7 baje ka alarm laga do")
        self.assertEqual(c1["intent"], "set_alarm")
        self.assertEqual(c1["arguments"]["time_str"], "07:00")

        # Calling intent
        c2 = classify_intent("Papa ko call lagao")
        self.assertEqual(c2["intent"], "call_contact")
        self.assertEqual(c2["arguments"]["name"], "Papa")

        # Weather intent
        c3 = classify_intent("Jaipur me mausam kaisa hai?")
        self.assertEqual(c3["intent"], "get_weather")
        self.assertEqual(c3["arguments"]["city"], "Jaipur")

        # Memory store intent
        c4 = classify_intent("my name is Nivesh")
        self.assertEqual(c4["intent"], "remember_fact")
        self.assertEqual(c4["arguments"]["value"], "Nivesh")

    def test_09_multi_step_planner(self):
        prompt = "Tomorrow wake me up at 7 AM, check the weather in Jaipur, and remind me to email my professor at 10 AM"
        plan = task_planner.plan(prompt)
        self.assertTrue(plan["is_multi_step"])
        self.assertGreaterEqual(plan["total_steps"], 3)
        self.assertEqual(plan["steps"][0]["intent"], "set_alarm")
        self.assertEqual(plan["steps"][1]["intent"], "get_weather")
        self.assertEqual(plan["steps"][2]["intent"], "add_reminder")

    def test_10_agent_orchestrator_end_to_end(self):
        prompt = "Kal subah 7 baje ka alarm laga do"
        result = orchestrator.process(prompt, mode="test")
        self.assertIn("spoken_response", result)
        self.assertGreater(len(result["executed_tools"]), 0)
        self.assertEqual(result["executed_tools"][0]["tool"], "set_alarm")

    def test_11_bare_math_and_conversions(self):
        # Bare multiplication
        c1 = classify_intent("165*92")
        self.assertEqual(c1["intent"], "calculate")
        self.assertEqual(c1["arguments"]["expression"], "165*92")

        res1 = orchestrator.process("165*92")
        self.assertIn("15180", res1["spoken_response"])
        self.assertEqual(res1["executed_tools"][0]["tool"], "calculate")

        # Bare division
        c2 = classify_intent("165/3")
        self.assertEqual(c2["intent"], "calculate")
        self.assertEqual(c2["arguments"]["expression"], "165/3")

        res2 = orchestrator.process("165/3")
        self.assertIn("55", res2["spoken_response"])
        self.assertEqual(res2["executed_tools"][0]["tool"], "calculate")

        # Hindi phrasing
        c3 = classify_intent("165 into 92")
        self.assertEqual(c3["intent"], "calculate")
        res3 = orchestrator.process("165 into 92")
        self.assertIn("15180", res3["spoken_response"])

    def test_12_datetime_intelligence(self):
        # Date query
        c1 = classify_intent("today date")
        self.assertEqual(c1["intent"], "get_current_datetime")

        res1 = orchestrator.process("today date")
        self.assertEqual(res1["executed_tools"][0]["tool"], "get_current_datetime")
        self.assertIn("date", res1["spoken_response"].lower())

        # Time query
        c2 = classify_intent("current time")
        self.assertEqual(c2["intent"], "get_current_datetime")

        res2 = orchestrator.process("current time")
        self.assertEqual(res2["executed_tools"][0]["tool"], "get_current_datetime")
        self.assertIn("time", res2["spoken_response"].lower())

    def test_13_assistant_identity(self):
        res1 = orchestrator.process("who are you")
        self.assertIn("IITIAN", res1["spoken_response"])

        res2 = orchestrator.process("who created you")
        self.assertIn("Nivesh Kumar Meena", res2["spoken_response"])

if __name__ == "__main__":
    unittest.main()
