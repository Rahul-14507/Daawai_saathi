# Dawai Saathi (దవై साथी) 💊
> **Voice-First Medicine Companion for Rural India**  
> *Built for the Gnani AI Hackathon | Real Deal • Main Character • Mixed Vibes • Jugaad Genius*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Gnani AI](https://img.shields.io/badge/Voice%20AI-Gnani.ai-indigo)](https://vachana.ai)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Problem Statement

In rural and semi-urban India, **over 65% of patients cannot read handwritten English prescriptions**. Elder patients frequently mix up morning and night dosages, forget antibiotic completion courses, or miss critical food restrictions (e.g. taking antacids on an empty stomach).

Their children or relatives often work in distant cities (e.g. Bengaluru, Hyderabad, Mumbai, Delhi) and struggle to ensure their parents take the right medications on time. Conventional alarm apps sound clinical, impersonal, and get ignored.

**Dawai Saathi solves this with empathetic, voice-first regional AI**:
1. **Prescription to Voice in Mother Tongue**: Converts complex doctor prescriptions and lab reports into a warm, simple audio explanation in 10 Indian languages via **Gnani AI TTS**.
2. **Hero Feature — Cloned Family Voice Reminders**: With explicit consent, a family member records 15 seconds of their voice. Dawai Saathi uses **Gnani Voice Cloning** to deliver dose reminders in *that specific relative's voice* (e.g., *"Amma, take your white tablet after lunch"*).
3. **Conversational Voice Q&A**: Elderly patients can ask questions by voice in code-mixed languages (Hinglish/Tanglish). Dawai Saathi transcribes with **Gnani Prisma v3.0 STT** and answers strictly from the prescription.

---

## 2. Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Client ["Mobile Web Client (360px+)"]
        UI_Scan["📸 Photo Upload / Camera"]
        UI_QnA["🎙️ Mic Recording (MediaRecorder)"]
        UI_Voice["🗣️ Family Voice Enrollment"]
        UI_Reminders["⏰ Daily Schedule & WhatsApp"]
    end

    subgraph Backend ["FastAPI Backend (Python 3.10+)"]
        Router["API Gateway / Routers"]
        AudioConv["FFmpeg (Browser WebM -> 16kHz WAV)"]
        Safety["Medical Safety & Consent Verifier"]
        DB[(SQLite Persistent Storage)]
        AudioCache[(SHA-256 Audio Cache)]
    end

    subgraph AI_Services ["AI Inference Services"]
        VisionLLM["Vision LLM (Gemini / Claude)"]
        GnaniTTS["Gnani Timbre TTS (Stock Voices)"]
        GnaniVC_Emb["Gnani VC Embeddings (/api/v1/tts/voice-clone/embeddings)"]
        GnaniVC_TTS["Gnani Cloned TTS (vachana-vc-v1)"]
        GnaniSTT["Gnani Prisma v3.0 (indic-auto STT)"]
    end

    UI_Scan -->|Upload Prescription| Router
    Router --> VisionLLM
    VisionLLM -->|Strict JSON Schema| Safety
    Safety --> DB
    Safety -->|Warm Script| GnaniTTS
    GnaniTTS -->|WAV Audio| AudioCache
    AudioCache -->|Play Audio| UI_Scan

    UI_Voice -->|15s Voice + Explicit Consent| AudioConv
    AudioConv --> GnaniVC_Emb
    GnaniVC_Emb -->|Speaker Embedding [1, 768]| DB

    UI_Reminders -->|Approve Template Scripts| GnaniVC_TTS
    DB -.->|Inject Speaker Embedding| GnaniVC_TTS
    GnaniTTS -.->|Prepend Spoken AI Disclaimer| GnaniVC_TTS
    GnaniVC_TTS -->|Cloned WAV| AudioCache
    AudioCache -->|Voice Reminder| UI_Reminders

    UI_QnA -->|Question Voice Clip| AudioConv
    AudioConv --> GnaniSTT
    GnaniSTT -->|Native Transcript| Safety
    DB -.->|Prescription Context Only| Safety
    Safety --> GnaniTTS
    GnaniTTS -->|Voice Reply| UI_QnA
```

---

## 3. Gnani AI APIs Used

| Capability | Gnani Endpoint | Model / Parameters | Usage in Dawai Saathi |
| :--- | :--- | :--- | :--- |
| **Stock Voice TTS** | `POST https://api.vachana.ai/api/v1/tts/inference` | `timbre-v2.5` & `timbre-v3.0`<br>Voices: `Suhana` (te-IN), `Chitra` (hi-IN), `Asmita` (ta-IN), `Chetana` (all 10 langs) | Explains prescription in warm, village-level vocabulary in patient's native tongue. |
| **Voice Clone Embeddings** | `POST https://api.vachana.ai/api/v1/tts/voice-clone/embeddings` | `multipart/form-data`<br>`audio_file`: 10-30s WAV | Extracts `speaker_embedding` (`[1, 768]`, `torch.bfloat16`) once per family member and caches in SQLite. |
| **Voice Cloned TTS** | `POST https://api.vachana.ai/api/v1/tts/inference` | `vachana-vc-v1`<br>`speaker_embedding`: stored tensor | Voices approved dose reminder templates in the family member's cloned voice. |
| **Speech-to-Text (STT)** | `POST https://api.vachana.ai/stt/v3` | `prisma-v3.0`<br>`language_code: indic-auto` | Transcribes patient's spoken questions with support for code-mixed Tanglish/Hinglish. |

> **Concurrency & Rate-Limit Handling**:  
> Per live Gnani documentation, active requests are serialized via thread-safe mutex locks to respect single-stream limits and prevent HTTP 429 errors. All synthesized audio files are cached on disk by `SHA256(text + voice)` to preserve API credits.

---

## 4. Non-Negotiable Medical Safety & Consent Design

1. **Strict Prescription Bounding**:
   - The LLM's system prompt strictly prohibits diagnosing, changing doses, suggesting new medications, or giving speculative advice.
   - Ambiguous handwriting or items with confidence `< 0.7` are automatically placed in a prominent yellow **"Please Confirm with Pharmacist"** warning box.
   - Emergency warning symptoms are prominently surfaced in a high-visibility red box.
2. **Cloned Voice Safeguards (No Medical Claims in Relative's Voice)**:
   - Free-form clinical explanations are **never** voiced in a cloned voice (stock regional voices are always used).
   - Cloned family voices are **strictly restricted to pre-approved template scripts** (e.g. *"{Call_name}, take {Medicine} after lunch"*).
   - Every cloned reminder audio carries a spoken stock AI disclaimer tag: *"This is an AI-generated reminder."*
3. **Explicit Consent & Privacy**:
   - Voice enrollment requires a mandatory affirmative consent checkbox.
   - Voice embeddings are stored locally in SQLite with ISO timestamp and can be permanently deleted anytime via the **"Delete my voice"** button.
4. **Graceful Offline & Rate Degradation**:
   - If Gnani or LLM APIs are offline or rate-limited, the system degrades smoothly to rule-based fallback responses and gentle chimes without UI disruption.

---

## 5. Quickstart & Local Setup

### Prerequisites
- Python 3.10+
- FFmpeg installed on system (verified automatically by application)

### 1. Clone & Install
```bash
git clone https://github.com/rahulpujari/dawai-saathi.git
cd Dawai
python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
# Gnani AI API Key (from https://vachana.ai)
GNANI_API_KEY=your_gnani_api_key_here

# Vision LLM Provider ("gemini" or "anthropic")
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_or_anthropic_api_key_here
LLM_MODEL=gemini-2.5-flash

PORT=8000
HOST=0.0.0.0
```

### 3. Step 0: Run Gnani API Smoke Test
```bash
python scripts/smoke_test.py
```
*Validates Stock TTS, Voice Clone Embeddings, Cloned TTS, and Prisma STT against live Gnani endpoints.*

### 4. Run End-to-End Pipeline Tests
```bash
python scripts/test_flow.py
```

### 5. Launch Application
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in any desktop or mobile browser.

---

## 6. One-Command Live Deployment

### Option A: Docker
```bash
docker build -t dawai-saathi .
docker run -p 8000:8000 --env-file .env dawai-saathi
```

### Option B: Deploy to Railway / Render / Fly.io
The repository includes a ready `Dockerfile` and `requirements.txt`:
1. Connect your GitHub repository to [Railway.app](https://railway.app) or [Render.com](https://render.com).
2. Set Environment Variables: `GNANI_API_KEY`, `LLM_API_KEY`, `LLM_PROVIDER`.
3. Set Build Command: Dockerfile (auto-detected).
4. Access your live public URL!

---

## 7. Limitations & Honest Hacks

- **Browser Audio Conversion**: Mobile browser WebM recordings are transcoded on the backend using FFmpeg into 16 kHz mono 16-bit PCM WAV.
- **Voice Cloned Indian Scripts**: While Timbre stock models support all 10 Indian scripts natively, cloned voices perform with highest naturalness on romanized Hindi/Telugu or regional scripts.
- **Microphone Permissions**: Web MediaRecorder requires HTTPS when deployed to a live domain or `localhost` during development.

---

## 8. Future Roadmap

- 📞 **IVR & Missed-Call Reminders**: Connect Gnani Voice Agent / Twilio SIP trunk to place real outbound automated calls to simple feature phones.
- 💬 **WhatsApp Automated Audio Notes**: Send the voice-cloned reminders directly as voice messages via WhatsApp Business API.
- 👩‍⚕️ **ASHA Worker Offline Mode**: Tablet-based local model caching for community health workers conducting village rounds with intermittent 2G/3G connectivity.
- 🔔 **Smart Pillbox IoT Integration**: ESP32 bluetooth pillbox that triggers the cloned voice when a compartment lid opens late.

---

## 9. License & Disclaimers

This project is licensed under the MIT License.  
**Disclaimer**: *Dawai Saathi is an educational and supportive tool designed to improve health literacy and medicine adherence. It explains what is written on prescriptions and does NOT diagnose, prescribe, or replace qualified medical practitioners.*
