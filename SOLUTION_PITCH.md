# Dawai Saathi (दवाई साथी / మందుల సహచరి)
### *Voice-First Medicine Companion for Bharat Powered by Gnani AI*

---

### 1. The Problem
In India, over **80% of elderly and rural patients** cannot read English handwritten doctor prescriptions. At the same time, millions of adult children migrate to cities for work, constantly anxious about whether their aging parents took their blood pressure or diabetes tablets before or after food.

Standard reminder apps fail in Bharat:
* **Literacy Barrier:** They rely on English UI and medical shorthand.
* **Cold Engagement:** Generic phone alarms are routinely ignored or silenced by elderly patients.
* **Dangerous Hallucinations:** Generic health chatbots often hallucinate medication advice without doctor supervision.

---

### 2. The Solution
**Dawai Saathi** bridges this healthcare literacy divide with a voice-first, vernacular assistant built natively on **Gnani AI's Sovereign Speech Stack**:

```
[ Handwritten Prescription / Lab Report ]
                   │
                   ▼  (Clinical Vision Parser)
[ Doctor-Bounded Medicines, Dosages & Food Timings ]
   ├──► 1. Regional Audio Summary (Gnani Timbre v2.5 - 10 Indian Languages)
   ├──► 2. Voice-Cloned Family Reminders (Gnani Vachana vc-v1 + Safety Tag)
   └──► 3. Spoken Follow-Up Q&A (Gnani Prisma v3.0 STT + Clinical Bounding)
```

---

### 3. Core Features

| Feature | Powered By | Clinical Impact |
| :--- | :--- | :--- |
| **Spoken Prescription Summary** | **Gnani Timbre v2.5** | Converts complex prescriptions into warm, spoken explanations in Telugu, Hindi, Tamil, Kannada, and 6 more Indian languages. |
| **Hero Feature: Family Voice Reminders** | **Gnani Vachana (`vachana-vc-v1`)** | A son or daughter records 10s of speech. Daily dose reminders play in their **actual cloned voice**: *"Mummy, take Pantoprazole before breakfast."* Studies show familiar family voices boost adherence by **80%+**. |
| **Prescription-Bounded Voice Q&A** | **Gnani Prisma v3.0 STT** | Patients tap the mic to ask code-mixed questions (*"Can I take this on an empty stomach?"*). Answers are strictly constrained to the prescription. |

---

### 4. Responsible AI & Clinical Safety Guardrails
1. **Explicit Voice Consent:** Enrolling a voice requires mandatory consent verification to prevent impersonation.
2. **Strict Template Bounding:** Cloned voices **never** speak unapproved text; they exclusively voice doctor-verified dosage slots.
3. **Mandatory Spoken AI Tag:** Every cloned audio note appends a concise safety tag at the end (*"AI Reminder / ఏఐ రిమైండర్"*).
4. **Clinical Fallback Matrix:** Out-of-bounds questions trigger yellow pharmacist warnings or red emergency doctor referrals.

---

### 5. Deployment & Tech Stack
* **AI Core:** Gnani AI Sovereign Stack (Prisma STT, Timbre v2.5 TTS, Vachana Voice Cloning).
* **Backend:** FastAPI, SQLite, FFmpeg 16kHz mono audio processing, thread-safe rate limiting.
* **Frontend:** Offline-ready, mobile-first Progressive Web App (PWA) with one-tap installation on Android/iOS.
* **Live Deployment:** Production container hosted on Render (`https://daawai-saathi.onrender.com`).
* **Source Code:** [github.com/Rahul-14507/Daawai_saathi](https://github.com/Rahul-14507/Daawai_saathi)

