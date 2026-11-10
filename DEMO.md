# 🎬 Dawai Saathi — Demo Day & Hackathon Presentation Pack

## 1. 60-Second Demo Video Script & Shot List

**Target Awards:** *Real Deal* (Rural Health Impact), *Main Character* (Regional Indian Languages), *Mixed Vibes* (Code-mixed STT), *Jugaad Genius* (Cloned Voice Reminders), *Demo Day Drop* (60s Pitch).

**Tone:** Urgent, empathetic, high energy, grounded in rural India reality.

| Timestamp | Visual / Screen Action | Spoken Voiceover / Audio | Key On-Screen Callout |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:08** | Split screen: Close-up of illegible English doctor's prescription vs an elderly mother in a village squinting at medicine bottles with confusion. | *"In rural India, millions of elderly parents receive prescriptions in English handwriting they cannot read. Their children work hundreds of kilometers away in cities, constantly worried."* | **The Problem: Illiterate & Confused by Prescriptions** |
| **00:08 - 00:20** | User opens Dawai Saathi on phone. Taps **"⚡ Load Sample Prescription"**. Instant animation analyzes medicines. | *"Introducing **Dawai Saathi**. Upload a photo. Our vision engine reads the prescription, and Gnani AI speaks the explanation in her mother tongue."* | **Gnani Timbre TTS (Telugu, Hindi, Tamil + 7 langs)** |
| **00:20 - 00:32** | Phone speaker plays warm Telugu voice: *"నమస్కారం లక్ష్మి దేవి గారూ. డాక్టర్ గారు మీకు నాలుగు రకాల మందులు రాశారు..."* UI highlights medicine cards & dosage icons. | *(Audio plays crisp regional voice explanation). "No confusing medical jargon. Clear dosages, food timings, and red-flag emergency symptoms."* | **Zero Jargon • Pure Native Voice Guidance** |
| **00:32 - 00:46** | **HERO FEATURE:** Son in Bengaluru opens "Family Voice", records 15s (*"Amma, take the tablet after lunch..."*), checks consent box. Screen switches to mother's daily schedule: plays reminder in **his exact cloned voice** with AI safety disclaimer. | *"Now the hero feature: The son records 15 seconds of his voice. With explicit consent, Gnani Voice Cloning creates personalized reminders: 'Amma, take your white tablet after lunch.' In her son's voice."* | **Hero Jugaad: Gnani Voice Cloning (`vachana-vc-v1`)** |
| **00:46 - 00:54** | Patient taps microphone, asks question in Tanglish/Hinglish: *"ఈ మందులు ఎప్పుడు వేసుకోవాలి?"* App transcribes via Gnani Prisma v3.0 and answers strictly from prescription. | *"She can ask follow-up questions by voice in code-mixed dialect. Dawai Saathi answers strictly from the prescription, never guessing."* | **Gnani Prisma v3.0 Code-Mixed STT** |
| **00:54 - 01:00** | Mother smiles, taps "Mark Taken", clicks "Share on WhatsApp". App persistent footer visible: *Medical explanation, not doctor replacement.* | *"Dawai Saathi: Giving every rural Indian patient a caring doctor's clarity and their family's voice. Built for the Gnani AI Hackathon."* | **Dawai Saathi • Built with Gnani AI** |

---

## 2. LinkedIn Post Draft

```markdown
🚀 What happens when an elderly mother in a rural village can't read her English prescription, while her son works 800 km away in a metro city?

Medical non-adherence in rural India isn't just a communication gap—it's a heartbreaking reality.

Proud to present **Dawai Saathi (दवाई साथी)**, built for the Gnani AI Hackathon! 💊🇮🇳

Dawai Saathi is a voice-first healthcare companion designed for the next billion users:
1️⃣ **Prescription Vision to Voice**: Patients snap a picture of their prescription or lab report. Dawai Saathi breaks down medications, timings, and food instructions into clear village-level language, spoken aloud via **Gnani AI Timbre TTS** across 10 Indian regional languages (Telugu, Hindi, Tamil, Kannada, Bengali, and more).
2️⃣ **The Hero Feature — Cloned Family Reminders**: A son or daughter records 10-20 seconds of their voice. With strict consent verification, Dawai Saathi clones their voice using **Gnani Voice Cloning (vachana-vc-v1)** to deliver affectionate daily dose reminders: *"Amma, take your medicine after lunch."*
3️⃣ **Code-Mixed Voice Q&A**: Patients ask follow-up questions by voice in code-mixed dialects (Hinglish/Tanglish). Powered by **Gnani Prisma v3.0 STT**, it transcribes naturally and answers strictly constrained to what the doctor wrote—never hallucinating.
4️⃣ **Ethical & Safety Guardrails**: Hardcoded medical safety boundaries, yellow alerts for ambiguous handwriting, and explicit consent logging for voice cloning.

Deep gratitude to the Gnani.ai team for building world-class speech and voice cloning models optimized for Indian languages! 

Check out the demo video and open-source repo below! 👇

#GreatIndianAIInternshipChallenge #GnaniAI #VoiceAI #HealthTech #BuildInPublic #AIForBharat #IndianLanguages #VoiceCloning
```

---

## 3. X (Twitter) Post / Thread Draft

**Tweet 1 (Hook & Video):**
> 70% of rural Indian patients struggle to read handwritten English prescriptions.
> 
> We built **Dawai Saathi (दवाई साथी)** for the @gnani_ai hackathon:
> 📸 Photo -> 10 Regional Languages Voice Explanation
> 🗣️ Son clones his voice -> Reminds his mother to take her pills on time!
> 
> Watch the 60s demo: 🧵👇
> #GreatIndianAIInternshipChallenge #GnaniAI

**Tweet 2 (Tech Stack):**
> How it works under the hood:
> 🎙️ **Speech-to-Text**: Gnani Prisma v3.0 (code-mixed dialect STT)
> 🗣️ **Text-to-Speech**: Gnani Timbre v2.5 / v3.0 (10 Indian regional languages)
> 🧬 **Voice Cloning**: Gnani VC Embeddings + `vachana-vc-v1` inference
> 🧠 **Prescription Parser**: Bounded Vision LLM with zero medical hallucinations
> ⚡ FastAPI + Mobile-first UI

**Tweet 3 (Hero Feature):**
> The Jugaad Genius:
> Instead of robotic alarms, the patient hears their son's affectionate voice: *"Amma, take the tablet after lunch."* 
> 
> Pre-approved medical templates only + mandatory consent + AI disclaimer tag. Tech with empathy. ❤️
