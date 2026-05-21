"""
IITIAN AI - Smart Messaging Tool
Supports WhatsApp deep linking, SMS preparation, and simulated message dispatch.
"""

import urllib.parse
from backend.tools.calling import get_contact
from backend.memory.storage import storage

def send_message(recipient: str, message: str, platform: str = "whatsapp") -> dict:
    """
    Sends or prepares a message to a contact via WhatsApp or SMS.
    """
    contact = get_contact(recipient)
    phone = contact["phone"] if contact else recipient
    contact_name = contact["name"] if contact else recipient

    clean_phone = "".join(filter(lambda c: c.isdigit(), phone))
    encoded_msg = urllib.parse.quote(message)

    # Build platform URLs
    wa_url = f"https://wa.me/{clean_phone}?text={encoded_msg}" if clean_phone else f"https://wa.me/?text={encoded_msg}"
    sms_url = f"sms:{clean_phone}?body={encoded_msg}"

    # Log to audit
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (timestamp, action, details, status)
            VALUES (datetime('now'), 'send_message', ?, 'success')
        """, (f"To: {contact_name} ({phone}) | Msg: {message}",))
        conn.commit()

    return {
        "success": True,
        "action": "send_message",
        "recipient": contact_name,
        "phone": phone,
        "message": message,
        "platform": platform,
        "whatsapp_url": wa_url,
        "sms_url": sms_url,
        "notification": f"Message drafted for {contact_name}: '{message}'",
        "voice_response": f"Message ready for {contact_name}: {message}."
    }
