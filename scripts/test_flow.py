"""
End-to-end integration test of Dawai Saathi API using FastAPI TestClient.
Tests:
1. Languages list
2. Prescription scan with sample image
3. Audio retrieval
4. Family voice enrollment with explicit consent
5. Cloned reminder generation & taken status toggle
6. Voice Q&A pipeline
"""
import io
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_full_pipeline():
    print("\n" + "=" * 60)
    print("RUNNING DAWAI SAATHI END-TO-END PIPELINE TEST")
    print("=" * 60)

    # 1. Test Languages
    resp = client.get("/api/languages")
    assert resp.status_code == 200
    langs = resp.json()
    assert len(langs) >= 10
    print(f"[PASS] 1. Languages loaded: {len(langs)} regional Indian languages available.")

    # 2. Test Scan Prescription
    with open("samples/sample_prescription.png", "rb") as f:
        img_bytes = f.read()
    
    resp = client.post(
        "/api/scan",
        files={"image": ("prescription.png", img_bytes, "image/png")},
        data={"language": "te-IN"}
    )
    assert resp.status_code == 200, resp.text
    rx_data = resp.json()
    rx_id = rx_data["prescription_id"]
    audio_url = rx_data["audio_url"]
    assert rx_id
    assert len(rx_data["data"]["medicines"]) >= 3
    print(f"[PASS] 2. Prescription scanned! Extracted {len(rx_data['data']['medicines'])} medicines.")
    print(f"       Spoken Summary (Telugu): {rx_data['spoken_summary'][:80]}...")

    # 3. Test Audio Endpoint
    audio_resp = client.get(audio_url)
    assert audio_resp.status_code == 200
    assert audio_resp.headers["content-type"] == "audio/wav"
    assert len(audio_resp.content) > 1000
    print(f"[PASS] 3. Spoken summary audio streamed ({len(audio_resp.content)} bytes, audio/wav).")

    # 4. Test Family Voice Enrollment (Consent = True)
    with open("samples/reference_speech.wav", "rb") as f:
        voice_bytes = f.read()

    resp = client.post(
        "/api/family/voice",
        files={"audio": ("family.wav", voice_bytes, "audio/wav")},
        data={
            "name": "Rahul (Son)",
            "patient_name": "Amma",
            "language": "te-IN",
            "consent": "true"
        }
    )
    assert resp.status_code == 200, resp.text
    v_data = resp.json()
    voice_id = v_data["voice_id"]
    assert voice_id
    print(f"[PASS] 4. Family voice enrolled with consent! Voice ID: {voice_id[:8]}...")

    # Test Consent Enforcement (Consent = False must be rejected)
    resp_no_consent = client.post(
        "/api/family/voice",
        files={"audio": ("family.wav", voice_bytes, "audio/wav")},
        data={
            "name": "Rahul (Son)",
            "patient_name": "Amma",
            "language": "te-IN",
            "consent": "false"
        }
    )
    assert resp_no_consent.status_code == 400
    print("[PASS] 4b. Mandatory consent check correctly rejected unconsented request.")

    # 5. Test Reminder Proposals & Generation
    resp = client.post(
        "/api/reminders/generate",
        json={
            "prescription_id": rx_id,
            "voice_id": voice_id,
            "patient_call_name": "Amma"
        }
    )
    assert resp.status_code == 200, resp.text
    reminders = resp.json()
    assert len(reminders) > 0
    rem_id = reminders[0]["id"]
    print(f"[PASS] 5. Cloned-voice reminders generated for {len(reminders)} dose slots.")
    print(f"       Slot: {reminders[0]['slot']}, Script: {reminders[0]['script_text'][:60]}...")

    # 6. Test Toggle Taken
    resp = client.post(f"/api/reminders/{rem_id}/toggle")
    assert resp.status_code == 200
    assert resp.json()["is_taken"] is True
    print(f"[PASS] 6. Dose marked as taken successfully.")

    # 7. Test Voice Q&A Pipeline
    resp = client.post(
        "/api/ask",
        files={"audio": ("q.wav", voice_bytes, "audio/wav")},
        data={
            "prescription_id": rx_id,
            "language": "indic-auto",
            "use_family_voice": "true"
        }
    )
    assert resp.status_code == 200, resp.text
    qna_res = resp.json()
    assert qna_res["answer_text"]
    assert qna_res["audio_url"]
    print(f"[PASS] 7. Voice Q&A verified:")
    print(f"       Transcript: {qna_res['transcript']}")
    print(f"       Answer: {qna_res['answer_text'][:80]}...")
    print(f"       Answer Audio: {qna_res['audio_url']}")

    print("\n" + "=" * 60)
    print("ALL 7 PIPELINE TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    test_full_pipeline()
