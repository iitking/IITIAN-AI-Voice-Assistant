"""
IITIAN AI - Calling and Contact Management Tool
Enables voice-driven phone calls, contact lookup, and contact directory management.
"""

import uuid
from backend.memory.storage import storage

def get_contact(name: str) -> dict:
    """Finds a contact by name or relation."""
    clean_name = name.strip().lower()
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, email, relation, notes FROM contacts")
        rows = cursor.fetchall()
        for r in rows:
            c_name = r["name"].lower()
            c_rel = (r["relation"] or "").lower()
            if clean_name in c_name or clean_name in c_rel or c_name in clean_name:
                return dict(r)
    return None

def list_contacts() -> list:
    """Returns all stored contacts."""
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, email, relation, notes FROM contacts ORDER BY name")
        return [dict(r) for r in cursor.fetchall()]

def add_contact(name: str, phone: str, relation: str = "", email: str = "", notes: str = "") -> dict:
    """Adds a new contact to the address book."""
    contact_id = str(uuid.uuid4())[:8]
    with storage._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (id, name, phone, email, relation, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                phone=excluded.phone,
                email=excluded.email,
                relation=excluded.relation,
                notes=excluded.notes
        """, (contact_id, name.strip(), phone.strip(), email.strip(), relation.strip(), notes.strip()))
        conn.commit()

    return {
        "success": True,
        "name": name,
        "phone": phone,
        "relation": relation,
        "message": f"Contact for {name} ({phone}) saved successfully."
    }

def call_contact(name: str) -> dict:
    """
    Initiates a phone call to a contact.
    Looks up phone number and returns call initiation data.
    """
    contact = get_contact(name)
    if contact:
        phone = contact["phone"]
        display_name = contact["name"]
        tel_url = f"tel:{phone.replace(' ', '')}"
        return {
            "success": True,
            "action": "call",
            "contact_name": display_name,
            "phone": phone,
            "relation": contact.get("relation", ""),
            "tel_url": tel_url,
            "message": f"Calling {display_name} ({phone})...",
            "voice_response": f"Calling {display_name} now."
        }
    else:
        # If not found in contacts, check if the argument itself is a phone number
        cleaned_num = "".join(filter(lambda c: c.isdigit() or c == "+", name))
        if len(cleaned_num) >= 7:
            return {
                "success": True,
                "action": "call",
                "contact_name": name,
                "phone": name,
                "tel_url": f"tel:{cleaned_num}",
                "message": f"Calling {name}...",
                "voice_response": f"Calling {name} now."
            }
        return {
            "success": False,
            "contact_name": name,
            "message": f"Contact '{name}' not found in address book.",
            "voice_response": f"Sorry, I couldn't find {name} in your contacts."
        }
