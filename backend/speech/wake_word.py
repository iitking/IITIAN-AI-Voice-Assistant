"""
IITIAN AI - Wake Word Verification
Validates whether a transcribed phrase begins with or contains wake triggers.
"""

from backend.config import WAKE_WORDS

def check_wake_word(transcription: str) -> tuple[bool, str]:
    """
    Checks if transcription contains wake words.
    Returns (is_wake, cleaned_query).
    """
    text_lower = transcription.strip().lower()
    for ww in WAKE_WORDS:
        if ww in text_lower:
            # Strip everything before and including wake word
            idx = text_lower.find(ww)
            cleaned = transcription[idx + len(ww):].strip(" ,:.-")
            return True, cleaned

    return False, transcription
