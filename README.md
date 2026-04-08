# 🤖 IITIAN — Your Personal AI Voice Assistant

<p align="center">
  <img src="https://img.shields.io/badge/AI-Agentic%20Voice%20Assistant-00f2fe?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Real--Time-Zero%20Latency-00df89?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Language-Hinglish%20%7C%20English%20%7C%20Hindi-7928ca?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <b>Listen. Understand. Remember. Think. Plan. Execute.</b>
</p>

<p align="center">
  An advanced, fully working Agentic AI Personal Voice Operating Layer designed and built by <b>Nivesh Kumar Meena</b>.
</p>

---

## 🌟 Overview

**IITIAN** is an Agentic AI Voice Assistant inspired by the vision of Apple Siri, Google Assistant, and ChatGPT Voice, elevated into an active personal operating companion.

Unlike traditional bots that only reply with text, **IITIAN thinks, plans, and takes real-world actions on your computer and phone**. It breaks down complex instructions into multi-step execution graphs, coordinates native device tools, manages your calendar and alarms, looks up contacts, sends WhatsApp messages, controls apps, and maintains persistent memories across sessions.

---

## ⚡ Key Highlights & Core Capabilities

| Capability | Description |
|---|---|
| 🎙️ **Real-Time Voice & Wake Word** | Continuous listening with **"Hey IITIAN"** wake word detection, Web Speech API integration, and natural voice responses. |
| 🧠 **Multi-Step Agentic Planning** | Decomposes compound instructions into sequential sub-tasks (e.g., *"Wake me up at 7 AM, check the weather, and remind me to email professor at 10 AM"*). |
| ⏰ **Smart Alarms & Countdown Timers** | Set alarms, running countdown timers with real-time SSE progress updates, and browser siren alerts. |
| 📞 **Calling & WhatsApp Messaging** | Integrated address book. Call contacts or generate pre-composed WhatsApp messages automatically. |
| 📅 **Calendar & Task Reminders** | Schedule meetings, view upcoming deadlines, track priority reminders, and mark tasks done. |
| 💻 **macOS & Desktop Automation** | Launch Chrome, VS Code, Terminal, Spotify; adjust system volume; monitor battery status; capture screenshots. |
| 📂 **Project Finder** | Locate and launch coding projects directly in VS Code or Finder (e.g. *"Mera laptop price predictor project open karo"*). |
| 🌦️ **Internet Intelligence** | Live weather forecasting (via Open-Meteo), Wikipedia/DuckDuckGo search, and safe calculator with unit conversions. |
| 💾 **Long-Term Memory Bank** | Remembers facts about you (name, college, habits, preferences) stored persistently in SQLite. |
| 🌐 **Zero-Dependency Architecture** | Runs 100% out of the box with standard Python 3.9+ and modern web standards! |

---

## 🏗️ System Architecture

```text
                                 🎤 USER (Voice / Text)
                                           |
                                           v
                             [ Continuous Wake Word Engine ]
                                  ("Hey IITIAN" / Push)
                                           |
                                           v
                             [ Web Speech STT Recognition ]
                                           |
                                           v
                             [ Natural Language Intent & ]
                             [    Entity Extraction      ]
                               (Hinglish / Hindi / English)
                                           |
                                           v
                             [ 🧠 Task Decomposition &   ]
                             [      Agent Planner        ]
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
                    v                      v                      v
             [ Device Tools ]       [ Web Intelligence ]   [ Memory Engine ]
             • Alarms & Timers      • Live Weather (Meteo) • User Profile
             • Calling & WhatsApp   • DuckDuckGo / Wiki    • Facts & Habits
             • Reminders & Calendar • Math & Conversions   • Session History
             • App Launcher (Chrome,• Project Finder       • SQLite Store
               VS Code, Terminal)
                    |                      |                      |
                    +----------------------+----------------------+
                                           |
                                           v
                             [ Action Execution & Audit ]
                                           |
                                           v
                           [ Conversational Response Synthesis ]
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
        [ Natural Text-to-Speech ]                  [ Futuristic Glassmorphism UI ]
         (Web Audio & SpeechSynth)                   (Glowing Voice Orb, Waveforms,
                                                      Live Console & Real-Time SSE)
```

---

## 🚀 Quickstart Guide

### 1. Launch the Real-Time Web Voice Assistant

Run one command:

```bash
python3 run.py
```

This will automatically launch the backend server at `http://127.0.0.1:8080` and open the futuristic Voice UI in your default browser!

### 2. Launch the Interactive Terminal Assistant

If you prefer using the terminal with native macOS speech synthesis:

```bash
python3 cli.py
```

### 3. Run the Automated Test Suite

```bash
python3 -m unittest tests/test_iitian.py
```

---

## 🗣️ Example Voice Commands

| Category | Example Voice Command (Hinglish & English) | Executed Tool |
|---|---|---|
| **Alarm** | *"Kal subah 7 baje ka alarm laga do"* | `set_alarm(time='07:00', label='Morning Alarm')` |
| **Timer** | *"Set a 5 minute timer for tea"* | `set_timer(duration_seconds=300, label='tea')` |
| **Calling** | *"Papa ko call lagao"* | `call_contact(name='Papa')` |
| **Messaging** | *"Papa ko message karo ki main 8 baje ghar aaunga"* | `send_message(recipient='Papa', message='...')` |
| **Reminder** | *"Kal 10 baje professor ko email yaad dilana"* | `add_reminder(text='email professor', time='...')` |
| **Meeting** | *"Schedule a meeting tomorrow at 11 AM"* | `add_calendar_event(title='Meeting', ...)` |
| **Weather** | *"Jaipur me mausam kaisa hai?"* | `get_weather(city='Jaipur')` |
| **Apps** | *"Open VS Code"* or *"Chrome kholo"* | `open_application(app_name='Visual Studio Code')` |
| **Project** | *"Mera laptop price predictor project open karo"* | `open_project(name='laptop price predictor')` |
| **System** | *"Battery status batao"* / *"Volume 50 percent karo"* | `get_battery_status()` / `set_volume(50)` |
| **Math** | *"Calculate 250 multiplied by 48"* | `calculate('250 * 48')` -> `12000` |
| **Units** | *"Convert 10 km to miles"* | `calculate('10 km to miles')` -> `6.21 miles` |
| **Memory** | *"Mera naam Nivesh hai"* -> *"Mera naam kya hai?"* | `remember_fact` -> `recall_fact` |
| **Multi-Step** | *"Tomorrow wake me up at 7 AM, check the weather, and remind me to email my professor at 10 AM"* | Decomposes into 3 sequential tool calls and executes them seamlessly! |

---

## 📁 Repository Structure

```text
idea 2/
├── README.md               # Main project documentation & user guide
├── requirements.txt        # Optional dependencies manifest
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── run.py                  # One-click master runner (starts server & opens browser)
├── cli.py                  # Interactive CLI assistant with macOS speech output
│
├── backend/
│   ├── main.py             # Server entrypoint
│   ├── server.py           # Threaded HTTP & SSE server
│   ├── config.py           # Configuration & identity settings
│   │
│   ├── agent/
│   │   ├── orchestrator.py # Central brain coordinating planning, tools & speech
│   │   ├── planner.py      # Multi-step task decomposition engine
│   │   └── intent.py       # Hinglish/English intent classifier & entity extractor
│   │
│   ├── tools/
│   │   ├── registry.py     # Unified tool registry & execution dispatcher
│   │   ├── alarm.py        # Alarms & countdown timers
│   │   ├── calling.py      # Contact directory & phone call initiator
│   │   ├── messaging.py    # WhatsApp & SMS deep-linking
│   │   ├── calendar.py     # Calendar meetings & scheduling
│   │   ├── reminders.py    # Priority reminders & completion tracking
│   │   ├── weather.py      # Live Open-Meteo weather forecasting
│   │   ├── web_search.py   # DuckDuckGo & Wikipedia search intelligence
│   │   ├── calculator.py   # Safe math, percentages & unit conversions
│   │   ├── computer.py     # macOS app launcher, volume, battery, screenshots
│   │   └── files.py        # Project finder & workspace explorer
│   │
│   ├── memory/
│   │   ├── storage.py      # SQLite database engine
│   │   └── memory_manager.py # Short-term context & long-term memory
│   │
│   └── speech/
│       ├── tts_engine.py   # Native macOS 'say' TTS bridge
│       └── wake_word.py    # Wake word verification helper
│
├── frontend/
│   ├── index.html          # Cyberpunk glassmorphic UI with dynamic voice orb
│   ├── styles.css          # Futuristic neon dark theme styling
│   └── app.js              # Web Speech API, audio synth, and real-time SSE client
│
├── tests/
│   ├── test_iitian.py      # Unit & integration test suite (10 test cases)
│   ├── test_server_inmemory.py # In-memory HTTP endpoint tests
│   └── test_server_live.py # Live network E2E test script
│
└── scripts/
    ├── start.sh            # Quick launcher script
    └── test.sh             # Quick test runner script
```

---

## 👨‍💻 Developer & Vision

Designed and developed by **Nivesh Kumar Meena**  
*B.Tech — Electrical Engineering*  
Focus: Artificial Intelligence • Agentic AI • Real-Time Systems • Deep Learning • NLP

> *"Don't just build an AI that talks. Build an AI that understands, remembers, thinks, plans, and takes action."*
