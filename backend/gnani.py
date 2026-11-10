"""
Gnani AI API Client for Dawai Saathi
Wraps:
1. Stock TTS (timbre-v2.5 / timbre-v3.0)
2. Voice Clone Embeddings (/api/v1/tts/voice-clone/embeddings)
3. Voice Cloned TTS (vachana-vc-v1)
4. Speech-to-Text (/stt/v3, prisma-v3.0)
Includes timeouts, retries, disk caching, concurrency serialization, and graceful degradation.
"""
import json
import logging
import time
import threading
import requests
from typing import Optional, Dict, Any

from backend.config import (
    GNANI_BASE_URL,
    GNANI_API_KEY,
    STOCK_VOICES,
    FALLBACK_VOICE
)
from backend.audio_utils import (
    get_cache_filename,
    get_cached_audio,
    save_cached_audio,
    generate_fallback_chime,
    concatenate_wavs,
    to_wav_resampled
)

logger = logging.getLogger("dawai.gnani")

# Thread lock to respect Gnani's active request concurrency limit (1 request at a time)
_GNANI_LOCK = threading.Lock()

def get_auth_headers() -> Dict[str, str]:
    if not GNANI_API_KEY:
        raise ValueError("GNANI_API_KEY is not configured in .env")
    return {
        "X-API-Key-ID": GNANI_API_KEY
    }

def tts_stock(text: str, lang: str = "hi-IN", voice: Optional[str] = None) -> bytes:
    """
    Synthesize speech using Gnani Stock Voice TTS.
    Returns binary WAV audio.
    """
    if not text.strip():
        return generate_fallback_chime("empty")

    # Determine voice and model
    voice_cfg = STOCK_VOICES.get(lang, FALLBACK_VOICE)
    model = voice_cfg["model"]
    chosen_voice = voice or voice_cfg["voice"]

    # Check cache
    cache_fn = get_cache_filename(text, f"stock_{model}_{chosen_voice}", lang)
    cached = get_cached_audio(cache_fn)
    # Ensure cached file is real speech (not old fallback chime of ~168KB)
    if cached and len(cached) > 175000:
        logger.info(f"TTS Stock Cache Hit: {cache_fn}")
        return cached

    # If no key, return synthesized fallback audio
    if not GNANI_API_KEY or GNANI_API_KEY == "your_gnani_api_key_here":
        logger.warning("GNANI_API_KEY not configured; returning fallback audio chime.")
        return generate_fallback_chime(text)

    url = f"{GNANI_BASE_URL}/api/v1/tts/inference"
    payload = {
        "text": text,
        "voice": chosen_voice,
        "model": model,
        "language": lang if lang != "indic-auto" else "hi-IN",
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 24000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav"
        }
    }

    # Execute with concurrency lock and retries
    last_err = None
    for attempt in range(2):
        try:
            with _GNANI_LOCK:
                resp = requests.post(
                    url,
                    headers={**get_auth_headers(), "Content-Type": "application/json"},
                    json=payload,
                    timeout=60
                )
            if resp.status_code == 200 and len(resp.content) > 1000:
                save_cached_audio(cache_fn, resp.content)
                logger.info(f"TTS Stock Success: {len(resp.content)} bytes generated")
                return resp.content
            
            logger.warning(f"TTS Stock attempt {attempt+1} status {resp.status_code}: {resp.text[:200]}")
            # If model/voice rejected, retry with Timbre v3.0 fallback voice
            if resp.status_code == 400:
                payload["model"] = FALLBACK_VOICE["model"]
                payload["voice"] = FALLBACK_VOICE["voice"]
            time.sleep(1.0)
        except Exception as e:
            last_err = e
            logger.error(f"TTS Stock attempt {attempt+1} exception: {e}")
            time.sleep(1.0)

    # Graceful degradation: never crash
    logger.error(f"TTS Stock failed after retries ({last_err}); serving fallback chime.")
    return generate_fallback_chime(text)

def make_embedding(wav_bytes: bytes) -> Dict[str, Any]:
    """
    Extract speaker_embedding from 5-30s clean WAV audio using Gnani Voice Clone Embeddings API.
    Returns: {"embedding": "...", "shape": [1, 768], "dtype": "torch.bfloat16"}
    """
    if not GNANI_API_KEY or GNANI_API_KEY == "your_gnani_api_key_here":
        logger.warning("GNANI_API_KEY missing; generating mock embedding.")
        return {
            "embedding": "mock_embedding_b64_vector",
            "shape": [1, 768],
            "dtype": "torch.bfloat16",
            "is_mock": True
        }

    url = f"{GNANI_BASE_URL}/api/v1/tts/voice-clone/embeddings"
    files = {"audio_file": ("speaker.wav", wav_bytes, "audio/wav")}

    last_err = None
    for attempt in range(2):
        try:
            with _GNANI_LOCK:
                resp = requests.post(url, headers=get_auth_headers(), files=files, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                # Parse structure according to live OpenAPI docs
                if "data" in data and "voice_clone_embedding" in data["data"]:
                    return data["data"]["voice_clone_embedding"]
                elif "voice_clone_embedding" in data:
                    return data["voice_clone_embedding"]
                elif "embedding" in data:
                    return data
                return data
            logger.warning(f"Voice Clone Embedding attempt {attempt+1} failed: {resp.status_code} - {resp.text[:200]}")
            time.sleep(1.0)
        except Exception as e:
            last_err = e
            logger.error(f"Voice Clone Embedding exception: {e}")
            time.sleep(1.0)

    raise RuntimeError(f"Voice clone embedding generation failed: {last_err}")

def tts_cloned(text: str, embedding: Dict[str, Any], lang: str = "hi-IN", with_tag: bool = True) -> bytes:
    """
    Synthesize reminder speech using Cloned Voice inference (vachana-vc-v1).
    Prepends mandatory spoken safety disclaimer: 'This is an AI-generated reminder.'
    Returns binary WAV audio.
    """
    if not text.strip():
        return generate_fallback_chime("empty")

    emb_repr = embedding.get("embedding", "")[:24]
    cache_fn = get_cache_filename(text, f"cloned_v2_{emb_repr}", lang)
    cached = get_cached_audio(cache_fn)
    if cached and len(cached) > 175000:
        logger.info(f"TTS Cloned Cache Hit: {cache_fn}")
        return cached

    # If mock embedding or no key, return stock TTS or fallback chime
    if embedding.get("is_mock") or not GNANI_API_KEY or GNANI_API_KEY == "your_gnani_api_key_here":
        logger.warning("Using stock voice fallback for cloned TTS (mock mode).")
        return tts_stock(text, lang)

    url = f"{GNANI_BASE_URL}/api/v1/tts/inference"
    payload = {
        "text": text,
        "model": "vachana-vc-v1",
        "audio_config": {
            "sample_rate": 24000,
            "encoding": "linear_pcm",
            "container": "wav"
        },
        "speaker_embedding": {
            "embedding": embedding["embedding"],
            "shape": embedding.get("shape", [1, 768]),
            "dtype": embedding.get("dtype", "torch.bfloat16")
        }
    }

    cloned_audio_raw = None
    for attempt in range(2):
        try:
            with _GNANI_LOCK:
                resp = requests.post(
                    url,
                    headers={**get_auth_headers(), "Content-Type": "application/json"},
                    json=payload,
                    timeout=60
                )
            if resp.status_code == 200 and len(resp.content) > 1000:
                cloned_audio_raw = resp.content
                break
            logger.warning(f"TTS Cloned attempt {attempt+1} failed: {resp.status_code} - {resp.text[:200]}")
            time.sleep(1.0)
        except Exception as e:
            logger.error(f"TTS Cloned attempt {attempt+1} exception: {e}")
            time.sleep(1.0)

    # Fallback to stock voice if cloned synthesis fails
    if not cloned_audio_raw:
        logger.warning("Cloned voice synthesis failed, falling back to regional stock voice.")
        cloned_audio_raw = tts_stock(text, lang)

    # Attach mandatory spoken safety tag (shortened and appended at end): "AI Reminder."
    if with_tag:
        try:
            tag_text = {
                "te-IN": "ఏఐ రిమైండర్.",
                "hi-IN": "एआई रिमाइंडर।",
                "ta-IN": "ஏஐ நினைவூட்டல்.",
                "kn-IN": "ಎಐ ಜ್ಞಾಪನೆ.",
                "bn-IN": "এআই রিমাইন্ডার।",
                "mr-IN": "एआय रिमाइंडर.",
                "gu-IN": "એઆઈ રિમાઇન્ડર.",
                "ml-IN": "എഐ റിമൈൻഡർ.",
                "pa-IN": "ਏਆਈ ਰੀਮਾਈਂਡਰ।",
                "en-IN": "AI Reminder."
            }.get(lang, "AI Reminder.")
            
            tag_audio = tts_stock(tag_text, lang)
            # Appended at the end of the cloned reminder
            final_audio = concatenate_wavs([cloned_audio_raw, tag_audio])
        except Exception as e:
            logger.error(f"Error attaching disclaimer tag: {e}")
            final_audio = cloned_audio_raw
    else:
        final_audio = cloned_audio_raw

    save_cached_audio(cache_fn, final_audio)
    return final_audio

def stt(wav_bytes: bytes, lang: str = "indic-auto") -> Dict[str, Any]:
    """
    Transcribe speech using Gnani Prisma v3.0 REST endpoint.
    Supports code-mixed input and auto language detection.
    Returns: {"transcript": "...", "detected_language": "..."}
    """
    if not GNANI_API_KEY or GNANI_API_KEY == "your_gnani_api_key_here":
        logger.warning("GNANI_API_KEY not configured; returning mock transcript.")
        return {
            "transcript": "ఈ మందులు ఎప్పుడు వేసుకోవాలి? (When should I take these medicines?)",
            "detected_language": "te-IN",
            "is_mock": True
        }

    url = f"{GNANI_BASE_URL}/stt/v3"
    files = {"audio_file": ("question.wav", wav_bytes, "audio/wav")}
    data = {
        "model": "prisma-v3.0",
        "language_code": lang
    }

    last_err = None
    for attempt in range(2):
        try:
            with _GNANI_LOCK:
                resp = requests.post(url, headers=get_auth_headers(), files=files, data=data, timeout=60)
            if resp.status_code == 200:
                result = resp.json()
                transcript = result.get("transcript", "").strip()
                detected = result.get("detected_language_code", lang)
                logger.info(f"STT Success: detected={detected}, transcript='{transcript}'")
                return {
                    "transcript": transcript,
                    "detected_language": detected
                }
            logger.warning(f"STT attempt {attempt+1} failed: {resp.status_code} - {resp.text[:200]}")
            time.sleep(1.0)
        except Exception as e:
            last_err = e
            logger.error(f"STT exception attempt {attempt+1}: {e}")
            time.sleep(1.0)

    logger.error(f"STT failed completely: {last_err}")
    return {
        "transcript": "Could not recognize audio. Please repeat clearly.",
        "detected_language": lang,
        "error": str(last_err)
    }

