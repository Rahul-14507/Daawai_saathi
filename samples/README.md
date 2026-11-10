# Dawai Saathi Sample Assets

This folder contains pre-generated realistic assets for rapid testing and hackathon demo evaluation:

1. `sample_prescription.png`:
   - A realistic Indian clinical prescription from "Arogya Seva Health Clinic" for patient Smt. Lakshmi Devi.
   - Contains: Pantoprazole 40mg (OD, before food), Paracetamol 650mg (TDS, after food), Amoxicillin 500mg (BD, after food), and Cough Syrup (night).
   - Click the **"⚡ Load Sample Prescription"** button in the web UI to test instant recognition and voice synthesis without needing a physical camera.

2. `reference_speech.wav`:
   - A 16 kHz mono 16-bit PCM reference speech waveform (6 seconds).
   - Used for Step 0 Gnani API smoke testing (`scripts/smoke_test.py`) and for voice clone embedding extraction tests.

### How to Add Your Own Prescription
- Place any clear photo of a doctor's handwritten or printed prescription/discharge summary into this folder or upload directly from the web interface.
