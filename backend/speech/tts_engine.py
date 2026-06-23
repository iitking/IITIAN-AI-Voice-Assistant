"""
IITIAN AI - Speech Engine
Provides local macOS 'say' TTS playback and speech synthesis bridge.
"""

import subprocess
import platform
import threading

def speak(text: str, voice: str = "Samantha", rate: int = 185) -> bool:
    """
    Speaks text aloud using native macOS speech engine.
    Runs asynchronously in a background thread to prevent blocking.
    """
    if platform.system() != "Darwin":
        return False

    def _speak_thread():
        try:
            # Check available voices or use default
            subprocess.run(["say", "-r", str(rate), text], timeout=15)
        except Exception:
            pass

    t = threading.Thread(target=_speak_thread, daemon=True)
    t.start()
    return True
