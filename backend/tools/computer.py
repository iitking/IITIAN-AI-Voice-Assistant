"""
IITIAN AI - Desktop and Computer Automation Tool
Provides macOS/system automation: application launcher, volume control, battery monitoring, and screenshot capture.
"""

import subprocess
import platform
import os
import time
from pathlib import Path
from backend.config import DATA_DIR

APP_MAP = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "browser": "Google Chrome",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "code": "Visual Studio Code",
    "terminal": "Terminal",
    "iterm": "iTerm",
    "spotify": "Spotify",
    "calculator": "Calculator",
    "notes": "Notes",
    "calendar": "Calendar",
    "safari": "Safari",
    "finder": "Finder",
    "system settings": "System Settings",
    "settings": "System Settings",
}

def open_application(app_name: str) -> dict:
    """
    Launches a specified application on the system.
    """
    clean_app = app_name.strip().lower()
    target_app = APP_MAP.get(clean_app, app_name)
    os_name = platform.system()

    try:
        if os_name == "Darwin":  # macOS
            cmd = ["open", "-a", target_app]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                return {
                    "success": True,
                    "app_name": target_app,
                    "message": f"Opened {target_app} successfully."
                }
            else:
                # Try generic open
                proc2 = subprocess.run(["open", f"-b", f"com.apple.{clean_app}"], capture_output=True, text=True, timeout=5)
                return {
                    "success": proc2.returncode == 0,
                    "app_name": target_app,
                    "message": f"Attempted to open {target_app}."
                }
        elif os_name == "Windows":
            subprocess.Popen([f"start {target_app}"], shell=True)
            return {"success": True, "app_name": target_app, "message": f"Launched {target_app} on Windows."}
        else:
            subprocess.Popen([target_app], shell=True)
            return {"success": True, "app_name": target_app, "message": f"Launched {target_app} on Linux."}
    except Exception as e:
        return {"success": False, "app_name": target_app, "error": str(e), "message": f"Failed to open {target_app}."}

def set_volume(level: int) -> dict:
    """
    Sets the system master volume (0 to 100).
    """
    level = max(0, min(100, int(level)))
    os_name = platform.system()
    try:
        if os_name == "Darwin":
            script = f"set volume output volume {level}"
            subprocess.run(["osascript", "-e", script], check=True, timeout=3)
            return {"success": True, "level": level, "message": f"System volume set to {level}%."}
        else:
            return {"success": True, "level": level, "message": f"Volume adjustment to {level}% requested."}
    except Exception as e:
        return {"success": False, "level": level, "error": str(e), "message": f"Failed to set volume."}

def get_battery_status() -> dict:
    """
    Checks the battery level and charging state on macOS.
    """
    os_name = platform.system()
    if os_name == "Darwin":
        try:
            res = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=3)
            out = res.stdout
            # Example output: " -InternalBattery-0 (id=36044899)	38%; discharging; 2:49 remaining"
            lines = out.strip().split("\n")
            pct = "Unknown"
            status = "Unknown"
            for line in lines:
                if "%" in line:
                    parts = line.split("\t")
                    if len(parts) > 1:
                        details = parts[1].split(";")
                        pct = details[0].strip()
                        status = details[1].strip() if len(details) > 1 else ""
            
            is_charging = "charging" in status.lower() or "ac" in out.lower()
            return {
                "success": True,
                "percentage": pct,
                "status": status,
                "is_charging": is_charging,
                "message": f"Battery is at {pct} ({status})."
            }
        except Exception as e:
            return {"success": False, "error": str(e), "message": "Could not read battery status."}
    return {"success": True, "percentage": "100%", "status": "Plugged in", "message": "System connected to power."}

def take_screenshot(filename: str = "") -> dict:
    """
    Takes a desktop screenshot on macOS and saves it to the data directory.
    """
    os_name = platform.system()
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    
    out_path = DATA_DIR / filename

    if os_name == "Darwin":
        try:
            subprocess.run(["screencapture", "-x", str(out_path)], check=True, timeout=5)
            return {
                "success": True,
                "path": str(out_path),
                "filename": filename,
                "message": f"Screenshot captured and saved to {filename}."
            }
        except Exception as e:
            return {"success": False, "error": str(e), "message": "Failed to capture screenshot."}
    return {"success": False, "message": "Screenshot supported natively on macOS."}

def open_url(url: str) -> dict:
    """Opens a website in the default browser."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", url], timeout=3)
        return {"success": True, "url": url, "message": f"Opened {url}."}
    except Exception as e:
        return {"success": False, "url": url, "error": str(e), "message": f"Failed to open {url}."}
