"""
Audio processing utilities: FFmpeg conversion, WAV concatenation, caching, and fallback audio.
"""
import hashlib
import io
import math
import struct
import subprocess
import wave
from pathlib import Path
from typing import Optional
from backend.config import FFMPEG_EXE, AUDIO_CACHE_DIR

def to_wav16k(raw: bytes) -> bytes:
    """
    Convert arbitrary browser/uploaded audio (WebM, OGG, MP3, AAC, etc.)
    to 16 kHz mono 16-bit PCM WAV for Gnani STT and VC embedding extraction.
    """
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-i", "pipe:0",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        "-f", "wav",
        "pipe:1"
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=raw,
            capture_output=True,
            check=True
        )
        return proc.stdout
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"FFmpeg conversion failed: {stderr_msg}") from e
    except FileNotFoundError:
        # If ffmpeg binary is somehow unavailable, return raw if it's already WAV
        if raw.startswith(b"RIFF"):
            return raw
        raise RuntimeError("FFmpeg is not installed or not found in PATH.")

def to_wav_resampled(raw: bytes, target_rate: int = 24000) -> bytes:
    """Convert audio to specified sample rate mono WAV."""
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-i", "pipe:0",
        "-ac", "1",
        "-ar", str(target_rate),
        "-c:a", "pcm_s16le",
        "-f", "wav",
        "pipe:1"
    ]
    try:
        proc = subprocess.run(cmd, input=raw, capture_output=True, check=True)
        return proc.stdout
    except Exception:
        return raw

def concatenate_wavs(wav_list: list[bytes]) -> bytes:
    """
    Concatenate multiple 16-bit PCM WAV byte streams into one seamless WAV file.
    Used to prepend the mandatory AI-generated notification tag to cloned reminders.
    """
    if not wav_list:
        return b""
    if len(wav_list) == 1:
        return wav_list[0]

    out_frames = bytearray()
    sample_rate = 24000
    channels = 1
    sample_width = 2

    for wav_bytes in wav_list:
        try:
            with wave.open(io.BytesIO(wav_bytes), "rb") as w:
                channels = w.getnchannels()
                sample_width = w.getsampwidth()
                sample_rate = w.getframerate()
                out_frames += w.readframes(w.getnframes())
        except Exception:
            pass

    out_io = io.BytesIO()
    with wave.open(out_io, "wb") as out_w:
        out_w.setnchannels(channels)
        out_w.setsampwidth(sample_width)
        out_w.setframerate(sample_rate)
        out_w.writeframes(out_frames)

    return out_io.getvalue()

def get_cache_filename(text: str, voice_or_emb: str, lang: str = "") -> str:
    """Generate deterministic SHA256 filename for audio caching."""
    key = f"{text}_{voice_or_emb}_{lang}".encode("utf-8")
    h = hashlib.sha256(key).hexdigest()[:24]
    return f"{h}.wav"

def get_cached_audio(filename: str) -> Optional[bytes]:
    """Retrieve audio from cache if exists."""
    p = AUDIO_CACHE_DIR / filename
    if p.exists() and p.stat().st_size > 0:
        return p.read_bytes()
    return None

def save_cached_audio(filename: str, audio_bytes: bytes) -> str:
    """Save audio bytes into cache directory and return filename."""
    p = AUDIO_CACHE_DIR / filename
    p.write_bytes(audio_bytes)
    return filename

def generate_fallback_chime(text: str = "", duration_sec: float = 3.5) -> bytes:
    """
    Generates a gentle melodic two-tone notification audio (WAV 24kHz mono)
    when Gnani TTS is unavailable or in mock test mode.
    """
    rate = 24000
    n_samples = int(rate * duration_sec)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / rate
            # Musical frequencies: E4 (330Hz), G#4 (415Hz), B4 (494Hz)
            phase = int(t * 3) % 3
            f = [330.0, 415.0, 494.0][phase]
            decay = max(0.0, 1.0 - (t % 1.0))
            sample = 0.5 * math.sin(2 * math.pi * f * t) * decay
            val = int(sample * 20000.0)
            frames += struct.pack("<h", max(-32767, min(32767, val)))
        w.writeframes(frames)
    return buf.getvalue()
