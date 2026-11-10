"""
SQLite Database Layer for Dawai Saathi
Stores:
- Prescriptions & Lab Reports
- Family Voice Clones (with explicit consent logging)
- Generated Medicine Reminders (with taken toggle)
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        # Prescriptions Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                language TEXT NOT NULL,
                image_path TEXT,
                data_json TEXT NOT NULL,
                spoken_summary TEXT NOT NULL,
                audio_filename TEXT
            );
        """)

        # Family Voice Profiles Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS family_voices (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                language TEXT NOT NULL,
                consent_given BOOLEAN NOT NULL DEFAULT 1,
                consent_timestamp TIMESTAMP NOT NULL,
                embedding_json TEXT NOT NULL,
                audio_path TEXT
            );
        """)

        # Dose Reminders Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                prescription_id TEXT NOT NULL,
                voice_id TEXT,
                slot TEXT NOT NULL,
                medicine_name TEXT NOT NULL,
                timing_description TEXT,
                script_text TEXT NOT NULL,
                audio_filename TEXT,
                is_taken BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE
            );
        """)
    conn.close()

# Initialize tables immediately
init_db()

# ==========================================
# Prescription CRUD
# ==========================================
def save_prescription(
    prescription_id: str,
    language: str,
    image_path: str,
    data: dict,
    spoken_summary: str,
    audio_filename: str
) -> str:
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO prescriptions 
            (id, language, image_path, data_json, spoken_summary, audio_filename)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                prescription_id,
                language,
                image_path,
                json.dumps(data, ensure_ascii=False),
                spoken_summary,
                audio_filename
            )
        )
    conn.close()
    return prescription_id

def get_prescription(prescription_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,)).fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    res["data"] = json.loads(res["data_json"])
    return res

def list_prescriptions(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT id, created_at, language, audio_filename, data_json FROM prescriptions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["data"] = json.loads(d["data_json"])
        out.append(d)
    return out

# ==========================================
# Family Voice CRUD
# ==========================================
def save_family_voice(
    name: str,
    patient_name: str,
    language: str,
    consent_given: bool,
    embedding: dict,
    audio_path: str
) -> str:
    if not consent_given:
        raise ValueError("Explicit consent is required to clone voice.")
    
    voice_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO family_voices 
            (id, name, patient_name, language, consent_given, consent_timestamp, embedding_json, audio_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                voice_id,
                name,
                patient_name,
                language,
                1 if consent_given else 0,
                now,
                json.dumps(embedding),
                audio_path
            )
        )
    conn.close()
    return voice_id

def get_family_voice(voice_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM family_voices WHERE id = ?", (voice_id,)).fetchone()
    conn.close()
    if not row:
        return None
    res = dict(row)
    res["embedding"] = json.loads(res["embedding_json"])
    return res

def list_family_voices() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, created_at, name, patient_name, language, consent_timestamp FROM family_voices ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_family_voice(voice_id: str) -> bool:
    conn = get_connection()
    with conn:
        cur = conn.execute("DELETE FROM family_voices WHERE id = ?", (voice_id,))
        deleted = cur.rowcount > 0
    conn.close()
    return deleted

# ==========================================
# Reminders CRUD
# ==========================================
def save_reminder(
    prescription_id: str,
    voice_id: Optional[str],
    slot: str,
    medicine_name: str,
    timing_description: str,
    script_text: str,
    audio_filename: str
) -> str:
    reminder_id = str(uuid.uuid4())
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO reminders
            (id, prescription_id, voice_id, slot, medicine_name, timing_description, script_text, audio_filename, is_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (reminder_id, prescription_id, voice_id, slot, medicine_name, timing_description, script_text, audio_filename)
        )
    conn.close()
    return reminder_id

def list_reminders_for_prescription(prescription_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reminders WHERE prescription_id = ? ORDER BY slot ASC",
        (prescription_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_reminder_taken(reminder_id: str) -> Optional[bool]:
    conn = get_connection()
    with conn:
        row = conn.execute("SELECT is_taken FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
        if not row:
            conn.close()
            return None
        new_status = 0 if row["is_taken"] else 1
        conn.execute("UPDATE reminders SET is_taken = ? WHERE id = ?", (new_status, reminder_id))
    conn.close()
    return bool(new_status)

