"""
FastAPI application for Dawai Saathi: Voice-first Medicine Helper for Rural India.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import (
    BASE_DIR,
    AUDIO_CACHE_DIR,
    UPLOADS_DIR,
    SUPPORTED_LANGUAGES,
    STOCK_VOICES
)
from backend.audio_utils import (
    to_wav16k,
    save_cached_audio,
    get_cache_filename
)
from backend import gnani
from backend import llm
from backend import db
from backend import reminder_templates

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dawai.main")

app = FastAPI(
    title="Dawai Saathi API",
    description="Voice-first medicine helper for rural Indian patients with Gnani AI TTS, STT, and Voice Cloning.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Pydantic Request Models
# ==========================================
class ApprovedReminderItem(BaseModel):
    slot: str
    script_text: str
    medicine_name: Optional[str] = "Prescribed Medicines"

class GenerateRemindersRequest(BaseModel):
    prescription_id: str
    voice_id: Optional[str] = None
    patient_call_name: Optional[str] = "Amma"
    approved_scripts: Optional[List[ApprovedReminderItem]] = None

# ==========================================
# Routes
# ==========================================
@app.get("/api/languages")
async def get_languages():
    """Return supported Indian regional languages."""
    return [
        {"code": code, "name": meta["name"], "native": meta["native"], "flag": meta["flag"]}
        for code, meta in SUPPORTED_LANGUAGES.items()
    ]

@app.get("/api/prescriptions")
async def get_prescriptions():
    """List recent prescriptions."""
    return db.list_prescriptions()

@app.get("/api/prescriptions/{prescription_id}")
async def get_single_prescription(prescription_id: str):
    p = db.get_prescription(prescription_id)
    if not p:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return p

# 1. Scan Prescription
@app.post("/api/scan")
async def scan_prescription(
    image: UploadFile = File(...),
    language: str = Form("te-IN")
):
    """
    Upload prescription/lab report photo.
    Extracts medicine details via Vision LLM and synthesizes regional spoken summary via Gnani Stock TTS.
    """
    logger.info(f"Scanning document: {image.filename}, language: {language}")
    
    if language not in SUPPORTED_LANGUAGES:
        language = "te-IN"

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Save uploaded image
    file_ext = Path(image.filename).suffix or ".png"
    img_filename = f"{uuid.uuid4()}{file_ext}"
    img_path = UPLOADS_DIR / img_filename
    img_path.write_bytes(image_bytes)

    # 1. Vision LLM extraction
    mime_type = image.content_type or "image/png"
    extracted_data = llm.extract_prescription(
        image_bytes=image_bytes,
        mime_type=mime_type,
        target_lang=language
    )

    # 2. Gnani TTS for spoken summary
    spoken_text = extracted_data.spoken_summary
    tts_audio = gnani.tts_stock(text=spoken_text, lang=language)
    
    # Save audio
    audio_fn = f"summary_{uuid.uuid4().hex[:12]}.wav"
    save_cached_audio(audio_fn, tts_audio)

    # 3. Store in DB
    rx_id = str(uuid.uuid4())
    db.save_prescription(
        prescription_id=rx_id,
        language=language,
        image_path=f"/uploads/{img_filename}",
        data=extracted_data.model_dump(),
        spoken_summary=spoken_text,
        audio_filename=audio_fn
    )

    return {
        "prescription_id": rx_id,
        "language": language,
        "data": extracted_data.model_dump(),
        "spoken_summary": spoken_text,
        "audio_url": f"/api/audio/{audio_fn}"
    }

# 2. Voice Q&A Follow-up
@app.post("/api/ask")
async def ask_question(
    audio: UploadFile = File(...),
    prescription_id: str = Form(...),
    language: str = Form("indic-auto"),
    use_family_voice: bool = Form(False)
):
    """
    Ask a voice follow-up question.
    Converts audio via ffmpeg -> Gnani STT (indic-auto) -> LLM answers from prescription -> TTS playback.
    """
    rx = db.get_prescription(prescription_id)
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")

    rx_lang = rx.get("language", "te-IN")
    raw_audio = await audio.read()
    if not raw_audio:
        raise HTTPException(status_code=400, detail="Empty audio recording.")

    # 1. Convert to 16kHz mono WAV
    try:
        wav_16k = to_wav16k(raw_audio)
    except Exception as e:
        logger.error(f"FFmpeg conversion error: {e}")
        raise HTTPException(status_code=400, detail=f"Audio conversion failed: {e}")

    # 2. Gnani STT
    stt_res = gnani.stt(wav_16k, lang="indic-auto")
    transcript = stt_res.get("transcript", "")
    detected_lang = stt_res.get("detected_language", rx_lang)
    logger.info(f"Question transcript: '{transcript}' (detected: {detected_lang})")

    # 3. LLM Answer constrained strictly to prescription context
    target_answer_lang = rx_lang if rx_lang in SUPPORTED_LANGUAGES else "te-IN"
    answer_text = llm.answer_prescription_question(
        question_text=transcript,
        prescription_data=rx["data"],
        target_lang=target_answer_lang
    )

    # 4. Synthesize voice answer
    # If family voice is requested and exists, use cloned voice; otherwise stock voice
    answer_audio_bytes = None
    if use_family_voice:
        voices = db.list_family_voices()
        if voices:
            v_full = db.get_family_voice(voices[0]["id"])
            if v_full:
                answer_audio_bytes = gnani.tts_cloned(
                    answer_text,
                    v_full["embedding"],
                    lang=target_answer_lang,
                    with_tag=True
                )

    if not answer_audio_bytes:
        answer_audio_bytes = gnani.tts_stock(answer_text, lang=target_answer_lang)

    ans_audio_fn = f"answer_{uuid.uuid4().hex[:12]}.wav"
    save_cached_audio(ans_audio_fn, answer_audio_bytes)

    return {
        "transcript": transcript,
        "detected_language": detected_lang,
        "answer_text": answer_text,
        "audio_url": f"/api/audio/{ans_audio_fn}"
    }

# 3. Family Voice Enrollment
@app.post("/api/family/voice")
async def create_family_voice(
    audio: UploadFile = File(...),
    name: str = Form(...),
    patient_name: str = Form("Amma"),
    language: str = Form("te-IN"),
    consent: bool = Form(...)
):
    """
    Enrolls a family member's voice with explicit consent.
    Calls Gnani VC Embeddings API and saves profile to database.
    """
    if not consent:
        raise HTTPException(
            status_code=400,
            detail="Consent is mandatory: You must agree that your voice will be used solely for medicine reminders."
        )

    raw_audio = await audio.read()
    if len(raw_audio) < 1000:
        raise HTTPException(status_code=400, detail="Voice recording is too short. Please speak 10-30 seconds.")

    # Convert to 16kHz WAV
    wav_16k = to_wav16k(raw_audio)

    # Save audio sample
    sample_fn = f"voice_sample_{uuid.uuid4().hex[:10]}.wav"
    sample_path = str(AUDIO_CACHE_DIR / sample_fn)
    save_cached_audio(sample_fn, wav_16k)

    # Call Gnani Voice Clone Embeddings API
    try:
        embedding = gnani.make_embedding(wav_16k)
    except Exception as e:
        logger.error(f"Voice embedding error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract voice clone embedding: {e}")

    voice_id = db.save_family_voice(
        name=name,
        patient_name=patient_name,
        language=language,
        consent_given=consent,
        embedding=embedding,
        audio_path=sample_path
    )

    return {
        "voice_id": voice_id,
        "name": name,
        "patient_name": patient_name,
        "language": language,
        "message": "Voice profile successfully enrolled and cached."
    }

@app.get("/api/family/voices")
async def list_family_voices():
    """List enrolled family voices."""
    return db.list_family_voices()

@app.delete("/api/family/voice/{voice_id}")
async def delete_family_voice(voice_id: str):
    """Delete a family voice profile and its embedding from database."""
    deleted = db.delete_family_voice(voice_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Voice profile not found.")
    return {"message": "Voice profile and embedding permanently deleted."}

# 4. Reminders Generation & Management
@app.post("/api/reminders/proposals")
async def get_reminder_proposals(
    prescription_id: str = Form(...),
    patient_call_name: str = Form("Amma")
):
    """
    Generate proposed dose scripts in patient language for family approval.
    """
    rx = db.get_prescription(prescription_id)
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")

    medicines = rx["data"].get("medicines", [])
    rx_lang = rx.get("language", "te-IN")

    proposals = reminder_templates.generate_reminder_proposals(
        medicines=medicines,
        lang=rx_lang,
        patient_call_name=patient_call_name
    )
    return proposals

@app.post("/api/reminders/generate")
async def generate_approved_reminders(req: GenerateRemindersRequest):
    """
    Takes approved dose reminder scripts and synthesizes audio.
    If voice_id is provided, uses Gnani Cloned Voice (vachana-vc-v1) with mandatory AI disclaimer tag!
    """
    rx = db.get_prescription(req.prescription_id)
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")

    rx_lang = rx.get("language", "te-IN")
    
    # Retrieve family voice if requested, or fallback to latest enrolled family voice
    family_voice = None
    if req.voice_id:
        family_voice = db.get_family_voice(req.voice_id)
    if not family_voice:
        voices = db.list_family_voices()
        if voices:
            family_voice = db.get_family_voice(voices[0]["id"])

    # Clear previous reminders for this prescription so fresh ones take effect
    conn = db.get_connection()
    with conn:
        conn.execute("DELETE FROM reminders WHERE prescription_id = ?", (req.prescription_id,))
    conn.close()

    # Determine scripts to synthesize
    scripts_to_voice = []
    if req.approved_scripts:
        for s in req.approved_scripts:
            scripts_to_voice.append({
                "slot": s.slot,
                "script_text": s.script_text,
                "medicine_name": s.medicine_name or "Prescribed Dose"
            })
    else:
        # Generate default proposals
        proposals = reminder_templates.generate_reminder_proposals(
            medicines=rx["data"].get("medicines", []),
            lang=rx_lang,
            patient_call_name=req.patient_call_name or "Amma"
        )
        for p in proposals:
            scripts_to_voice.append({
                "slot": p["slot"],
                "script_text": p["script_text"],
                "medicine_name": p["medicines_summary"]
            })

    results = []
    for item in scripts_to_voice:
        slot = item["slot"]
        script_text = item["script_text"]
        med_name = item["medicine_name"]

        # Synthesize audio (cloned if family voice, else stock)
        if family_voice:
            audio_bytes = gnani.tts_cloned(
                text=script_text,
                embedding=family_voice["embedding"],
                lang=rx_lang,
                with_tag=True
            )
            voice_label = f"Cloned: {family_voice['name']}"
        else:
            audio_bytes = gnani.tts_stock(text=script_text, lang=rx_lang)
            voice_label = "Stock Regional Voice"

        audio_fn = f"rem_{slot}_{uuid.uuid4().hex[:10]}.wav"
        save_cached_audio(audio_fn, audio_bytes)

        # Save to reminders DB
        rem_id = db.save_reminder(
            prescription_id=req.prescription_id,
            voice_id=req.voice_id,
            slot=slot,
            medicine_name=med_name,
            timing_description=slot.capitalize(),
            script_text=script_text,
            audio_filename=audio_fn
        )

        results.append({
            "id": rem_id,
            "slot": slot,
            "medicine_name": med_name,
            "script_text": script_text,
            "voice_label": voice_label,
            "audio_url": f"/api/audio/{audio_fn}",
            "is_taken": False
        })

    return results

@app.get("/api/reminders/{prescription_id}")
async def get_reminders(prescription_id: str):
    """Fetch existing dose reminders for a prescription."""
    items = db.list_reminders_for_prescription(prescription_id)
    for it in items:
        it["audio_url"] = f"/api/audio/{it['audio_filename']}"
    return items

@app.post("/api/reminders/{reminder_id}/toggle")
async def toggle_reminder(reminder_id: str):
    """Toggle dose taken status."""
    new_status = db.toggle_reminder_taken(reminder_id)
    if new_status is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"id": reminder_id, "is_taken": new_status}

# 5. Audio Serving
@app.get("/api/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve synthesized WAV audio files."""
    audio_path = AUDIO_CACHE_DIR / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

# Serve uploaded images
@app.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    img_path = UPLOADS_DIR / filename
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path=str(img_path))

# ==========================================
# Frontend Static Files & Samples
# ==========================================
FRONTEND_DIR = BASE_DIR / "frontend"
SAMPLES_DIR = BASE_DIR / "samples"

if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(
            str(FRONTEND_DIR / "index.html"),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

    @app.get("/manifest.json")
    async def serve_manifest():
        return FileResponse(
            str(FRONTEND_DIR / "manifest.json"),
            media_type="application/manifest+json"
        )

    @app.get("/sw.js")
    async def serve_sw():
        return FileResponse(
            str(FRONTEND_DIR / "sw.js"),
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/"}
        )

    @app.get("/icon-192.png")
    async def serve_icon_192():
        return FileResponse(str(FRONTEND_DIR / "icon-192.png"), media_type="image/png")

    @app.get("/icon-512.png")
    async def serve_icon_512():
        return FileResponse(str(FRONTEND_DIR / "icon-512.png"), media_type="image/png")

    @app.get("/apple-touch-icon.png")
    async def serve_apple_touch_icon():
        return FileResponse(str(FRONTEND_DIR / "apple-touch-icon.png"), media_type="image/png")

    @app.get("/favicon.png")
    @app.get("/favicon.ico")
    async def serve_favicon():
        return FileResponse(str(FRONTEND_DIR / "favicon.png"), media_type="image/png")
