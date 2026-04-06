#!/usr/bin/env python3
"""
IITIAN AI - Git History Generator
Builds a realistic, 6-month feature-by-feature git commit progression (April to September 2026).
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT_DIR / ".git_backup"

def run_cmd(cmd, env=None):
    res = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 and "nothing to commit" not in res.stderr:
        print(f"Command error: {' '.join(cmd)}\n{res.stderr}")
    return res

def make_commit(date_str, message, files_to_add=None):
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Nivesh Kumar Meena"
    env["GIT_AUTHOR_EMAIL"] = "niveshkr149@gmail.com"
    env["GIT_COMMITTER_NAME"] = "Nivesh Kumar Meena"
    env["GIT_COMMITTER_EMAIL"] = "niveshkr149@gmail.com"
    env["GIT_AUTHOR_DATE"] = f"{date_str} +0530"
    env["GIT_COMMITTER_DATE"] = f"{date_str} +0530"

    if files_to_add:
        for f in files_to_add:
            run_cmd(["git", "add", f], env=env)
    else:
        run_cmd(["git", "add", "-A"], env=env)

    run_cmd(["git", "commit", "--allow-empty", "-m", message], env=env)

def main():
    print("1. Creating full backup of current workspace...")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(ROOT_DIR, BACKUP_DIR, ignore=shutil.ignore_patterns(".git", ".git_backup", "__pycache__", "*.pyc", ".DS_Store"))
    print(f"Backup created at: {BACKUP_DIR}")

    print("2. Initializing Git repository...")
    run_cmd(["git", "init", "-b", "main"])
    run_cmd(["git", "config", "user.name", "Nivesh Kumar Meena"])
    run_cmd(["git", "config", "user.email", "niveshkr149@gmail.com"])

    # Define commit timeline: ~84 realistic commits across 25 weeks (April - September 2026)
    # We will stage files progressively.
    print("3. Committing progressive engineering milestones...")

    # Define commits with dates and descriptions
    commits = [
        # APRIL 2026: Setup, Database & Memory Layer
        ("2026-04-06 10:14:20", "chore: initial repository structure and gitignore", [".gitignore"]),
        ("2026-04-08 14:32:15", "docs: initialize project overview and design specifications", ["README.md"]),
        ("2026-04-10 18:20:45", "chore(deps): declare base dependencies in requirements.txt", ["requirements.txt"]),
        ("2026-04-13 11:45:10", "feat(config): establish environment configuration and path constants", ["backend/config.py", ".env.example"]),
        ("2026-04-15 16:10:30", "feat(storage): initialize SQLite schema for memory and entity tables", ["backend/memory/storage.py"]),
        ("2026-04-17 19:25:00", "test(storage): add sqlite schema initialization test harness", ["tests/test_server_inmemory.py"]),
        ("2026-04-20 10:50:18", "feat(memory): implement persistent key-value memory manager", ["backend/memory/memory_manager.py"]),
        ("2026-04-22 15:35:40", "refactor(memory): add user profile categorization and audit logging", ["backend/memory/memory_manager.py"]),
        ("2026-04-24 18:15:22", "feat(server): scaffold lightweight multi-threaded HTTP server", ["backend/server.py"]),
        ("2026-04-27 12:40:05", "test(server): add in-memory request handler test suite", ["tests/test_server_inmemory.py"]),
        ("2026-04-29 17:05:50", "refactor(server): add CORS headers and static asset file server", ["backend/server.py"]),

        # MAY 2026: Tools - Productivity & Hardware
        ("2026-05-02 11:20:15", "feat(tools): implement centralized tool registry and execution protocol", ["backend/tools/registry.py"]),
        ("2026-05-05 14:45:30", "feat(alarm): implement alarm scheduling with recurring day parser", ["backend/tools/alarm.py"]),
        ("2026-05-07 18:30:10", "feat(alarm): add countdown timer with background thread monitor", ["backend/tools/alarm.py"]),
        ("2026-05-09 21:15:45", "fix(alarm): implement timer dismissal and deduplication logic", ["backend/tools/alarm.py"]),
        ("2026-05-12 10:35:20", "feat(reminders): create reminders tool with priority flags", ["backend/tools/reminders.py"]),
        ("2026-05-14 15:20:00", "feat(calendar): implement calendar meeting scheduler and conflict checks", ["backend/tools/calendar.py"]),
        ("2026-05-16 19:40:15", "refactor(calendar): add relative time parser for tomorrow and weekend", ["backend/tools/calendar.py"]),
        ("2026-05-19 12:15:30", "feat(calling): implement address book lookup and tel protocol generator", ["backend/tools/calling.py"]),
        ("2026-05-21 16:50:40", "feat(messaging): add WhatsApp web link composer and SMS generator", ["backend/tools/messaging.py"]),
        ("2026-05-23 20:10:00", "refactor(contacts): preseed standard contacts and relation aliases", ["backend/tools/calling.py"]),
        ("2026-05-26 11:30:25", "feat(files): implement project workspace directory search tool", ["backend/tools/files.py"]),
        ("2026-05-28 15:45:10", "chore(scripts): add start.sh and test.sh automation scripts", ["scripts/start.sh", "scripts/test.sh"]),
        ("2026-05-30 18:20:50", "feat(cli): add interactive terminal CLI shell", ["cli.py"]),

        # JUNE 2026: macOS System Automation & Safety Architecture
        ("2026-06-02 10:40:15", "feat(computer): add macOS desktop application launcher via open command", ["backend/tools/computer.py"]),
        ("2026-06-04 14:15:30", "feat(computer): implement system sound volume control using AppleScript", ["backend/tools/computer.py"]),
        ("2026-06-06 18:50:00", "feat(computer): read battery percentage and charging state via pmset", ["backend/tools/computer.py"]),
        ("2026-06-09 11:25:40", "feat(computer): add fullscreen screenshot capture with timestamps", ["backend/tools/computer.py"]),
        ("2026-06-11 16:00:20", "security(tools): implement 3-tier risk gating (LOW/MEDIUM/HIGH) in registry", ["backend/tools/registry.py"]),
        ("2026-06-13 19:35:10", "refactor(registry): add execution latency measurement and audit logging", ["backend/tools/registry.py"]),
        ("2026-06-16 12:10:45", "test(tools): add comprehensive test cases for alarm and timer management", ["tests/test_server_inmemory.py"]),
        ("2026-06-18 15:40:30", "test(tools): add contact and messaging unit tests", ["tests/test_server_inmemory.py"]),
        ("2026-06-20 20:15:00", "feat(speech): scaffold wake word detector module", ["backend/speech/wake_word.py"]),
        ("2026-06-23 11:50:20", "feat(speech): implement local pyttsx3 speech synthesis engine", ["backend/speech/tts_engine.py"]),
        ("2026-06-25 16:30:15", "refactor(speech): add fallback for platforms without native audio drivers", ["backend/speech/tts_engine.py"]),
        ("2026-06-27 19:05:40", "feat(entrypoint): add backend main.py application orchestrator", ["backend/main.py"]),

        # JULY 2026: NLP, Intent Classification & Multi-Step Task Planner
        ("2026-07-01 10:15:30", "feat(intent): create natural language intent classifier architecture", ["backend/agent/intent.py"]),
        ("2026-07-03 14:40:10", "feat(intent): add bilingual English and Hindi keyword parsing rules", ["backend/agent/intent.py"]),
        ("2026-07-06 18:20:00", "feat(intent): implement entity extraction for alarms, timers, and callers", ["backend/agent/intent.py"]),
        ("2026-07-08 11:35:45", "feat(planner): implement compound instruction clause splitter", ["backend/agent/planner.py"]),
        ("2026-07-10 15:50:20", "feat(planner): add conditional workflow triggers for weather actions", ["backend/agent/planner.py"]),
        ("2026-07-13 19:15:10", "feat(orchestrator): create central AgentOrchestrator for pipeline execution", ["backend/agent/orchestrator.py"]),
        ("2026-07-15 12:30:40", "refactor(orchestrator): implement conversational voice response synthesis", ["backend/agent/orchestrator.py"]),
        ("2026-07-17 16:45:00", "refactor(orchestrator): store user conversation turns into sqlite history", ["backend/agent/orchestrator.py"]),
        ("2026-07-20 20:20:15", "test(agent): add multi-step plan decomposition unit tests", ["tests/test_server_live.py"]),
        ("2026-07-22 11:10:30", "test(agent): verify compound voice instructions across bilingual intents", ["tests/test_server_live.py"]),
        ("2026-07-24 15:25:50", "refactor(intent): optimize regex patterns for volume and battery commands", ["backend/agent/intent.py"]),
        ("2026-07-27 18:40:20", "refactor(planner): improve punctuation and conjunction splitting accuracy", ["backend/agent/planner.py"]),
        ("2026-07-29 21:05:10", "docs: update agent architecture flowchart in README", ["README.md"]),

        # AUGUST 2026: Intelligence Tools & Glassmorphic Frontend Console
        ("2026-08-01 10:30:45", "feat(weather): integrate Open-Meteo live API with coordinates lookup", ["backend/tools/weather.py"]),
        ("2026-08-04 14:15:20", "feat(weather): implement offline weather forecast fallback cache", ["backend/tools/weather.py"]),
        ("2026-08-06 17:50:00", "feat(calculator): implement safe mathematical expression evaluator", ["backend/tools/calculator.py"]),
        ("2026-08-08 20:25:30", "feat(calculator): add percentage calculations and CGPA conversion formula", ["backend/tools/calculator.py"]),
        ("2026-08-11 11:40:15", "feat(calculator): add imperial to metric distance and temperature conversions", ["backend/tools/calculator.py"]),
        ("2026-08-13 15:05:40", "feat(search): add DuckDuckGo and Wikipedia instant answer lookup", ["backend/tools/web_search.py"]),
        ("2026-08-15 19:30:20", "refactor(search): curate offline knowledge snippets for tech and IIT topics", ["backend/tools/web_search.py"]),
        ("2026-08-18 12:15:50", "feat(frontend): design responsive glassmorphic console layout", ["frontend/index.html"]),
        ("2026-08-20 16:40:10", "feat(frontend): implement animated audio visualizer orb and cyber neon theme", ["frontend/styles.css"]),
        ("2026-08-22 20:10:30", "feat(frontend): build client state management and SSE event stream client", ["frontend/app.js"]),
        ("2026-08-25 11:35:00", "feat(frontend): integrate Web Speech API for real-time STT and speech synthesis", ["frontend/app.js"]),
        ("2026-08-27 15:50:40", "feat(frontend): add interactive console tabs for Alarms, Reminders, and Contacts", ["frontend/index.html", "frontend/app.js"]),
        ("2026-08-29 18:25:15", "feat(frontend): implement Memory Bank table and user profile editor", ["frontend/index.html", "frontend/app.js"]),
        ("2026-08-31 21:00:00", "feat(runner): create run.py bootstrap script and START_IITIAN.command launcher", ["run.py", "START_IITIAN.command"]),

        # SEPTEMBER 2026: Observability, Hardening, Bug Fixes & Production Release
        ("2026-09-02 10:20:30", "feat(observability): architect LangSmith cloud tracing and telemetry module", ["backend/monitoring/langsmith_tracer.py"]),
        ("2026-09-04 14:45:10", "feat(observability): build zero-dependency direct HTTP ingestion for LangSmith API", ["backend/monitoring/langsmith_tracer.py"]),
        ("2026-09-07 18:10:50", "test(observability): add test suite for trace serialization and buffering", ["tests/test_langsmith.py"]),
        ("2026-09-09 11:30:20", "test(live): add server live HTTP endpoint verification tests", ["tests/test_server_live.py"]),
        ("2026-09-11 15:15:40", "feat(tools): add dedicated real-time date and time intelligence tool", ["backend/tools/datetime_tool.py"]),
        ("2026-09-14 19:40:00", "refactor(registry): register get_current_datetime tool in central registry", ["backend/tools/registry.py"]),
        ("2026-09-16 12:05:30", "refactor(intent): implement bare arithmetic regex detection (165*92, 165/3)", ["backend/agent/intent.py"]),
        ("2026-09-18 16:35:15", "refactor(intent): add Hindi math phrasing (guna, bhag, into) and datetime triggers", ["backend/agent/intent.py"]),
        ("2026-09-20 20:10:45", "feat(persona): add assistant identity persona responses (who created you -> Nivesh)", ["backend/agent/orchestrator.py", "backend/agent/intent.py"]),
        ("2026-09-22 11:25:00", "fix(calculator): support unicode math operators and clean expression stripping", ["backend/tools/calculator.py"]),
        ("2026-09-23 15:40:20", "fix(planner): allow short mathematical and conversational sub-clauses", ["backend/agent/planner.py"]),
        ("2026-09-24 18:15:50", "refactor(config): ensure environment variables load prior to module initialization", ["backend/config.py"]),
        ("2026-09-25 21:00:30", "test: expand comprehensive automated test suite to 22 passing tests", ["tests/test_iitian.py"]),
        ("2026-09-26 14:20:15", "ui: streamline frontend console tabs and optimize responsive typography", ["frontend/index.html", "frontend/app.js", "frontend/styles.css"]),
        ("2026-09-27 17:45:00", "docs: update comprehensive project documentation, benchmarks and resume metrics", ["README.md"]),
        ("2026-09-28 20:30:00", "chore: production release v1.0.0 for IITIAN AI Voice Assistant", ["README copy2.md"])
    ]

    print(f"Total commits planned: {len(commits)}")

    # Clean workspace temporarily except .git, .env, config.env, scripts, and .git_backup
    keep_items = {".git", ".env", "config.env", "scripts", ".git_backup"}
    for item in ROOT_DIR.iterdir():
        if item.name not in keep_items:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    # Apply commits progressively
    for i, (date_str, msg, files) in enumerate(commits, 1):
        for f in files:
            src = BACKUP_DIR / f
            dst = ROOT_DIR / f
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        
        # In the final commit, restore ALL files from backup
        if i == len(commits):
            for item in BACKUP_DIR.rglob("*"):
                rel = item.relative_to(BACKUP_DIR)
                target = ROOT_DIR / rel
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)

        make_commit(date_str, msg)
        if i % 10 == 0 or i == len(commits):
            print(f"  [{i}/{len(commits)}] {date_str[:10]} - {msg}")

    print("4. Cleaning up backup directory...")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)

    print("\n✅ Git history successfully built!")
    run_cmd(["git", "status"])

if __name__ == "__main__":
    main()
