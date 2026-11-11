"""
Application configuration for Dawai Saathi
"""
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Storage and Cache
OUT_DIR = BASE_DIR / "out"
AUDIO_CACHE_DIR = OUT_DIR / "audio_cache"
UPLOADS_DIR = OUT_DIR / "uploads"
DB_PATH = OUT_DIR / "dawai_saathi.db"

for d in [OUT_DIR, AUDIO_CACHE_DIR, UPLOADS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Gnani AI API Config
GNANI_BASE_URL = os.getenv("GNANI_BASE_URL", "https://api.vachana.ai").rstrip("/")
GNANI_API_KEY = os.getenv("GNANI_API_KEY", "").strip()

# LLM Config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# FFmpeg Binary Resolution
def find_ffmpeg() -> str:
    """Find ffmpeg executable from PATH or common install directories on Windows/Linux."""
    in_path = shutil.which("ffmpeg")
    if in_path:
        return in_path
    
    # Common Windows winget / localappdata path
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_path = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_path.exists():
            for p in winget_path.glob("**/ffmpeg.exe"):
                if p.is_file():
                    return str(p)
    
    # Standard fallback
    return "ffmpeg"

FFMPEG_EXE = find_ffmpeg()

# Regional Languages Supported by Gnani
SUPPORTED_LANGUAGES = {
    "te-IN": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "hi-IN": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
    "ta-IN": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "kn-IN": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "bn-IN": {"name": "Bengali", "native": "বাংলা", "flag": "🇮🇳"},
    "mr-IN": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳"},
    "gu-IN": {"name": "Gujarati", "native": "ગુજરાતી", "flag": "🇮🇳"},
    "ml-IN": {"name": "Malayalam", "native": "മലയാളം", "flag": "🇮🇳"},
    "pa-IN": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
    "en-IN": {"name": "English", "native": "English", "flag": "🌐"},
}

# Gnani Stock Voice Catalog
# Timbre v2.5 voices have dedicated language specializations.
# Timbre v3.0 voice 'Chetana' is empathetic healthcare voice that speaks all 10 languages.
STOCK_VOICES = {
    "te-IN": {"model": "timbre-v2.5", "voice": "Suhana"},
    "hi-IN": {"model": "timbre-v2.5", "voice": "Chitra"},
    "ta-IN": {"model": "timbre-v2.5", "voice": "Asmita"},
    "kn-IN": {"model": "timbre-v2.5", "voice": "Saanvi"},
    "bn-IN": {"model": "timbre-v2.5", "voice": "Kirra"},
    "mr-IN": {"model": "timbre-v2.5", "voice": "Zahira"},
    "gu-IN": {"model": "timbre-v2.5", "voice": "Falak"},
    "ml-IN": {"model": "timbre-v2.5", "voice": "Reshma"},
    "pa-IN": {"model": "timbre-v2.5", "voice": "Mehuli"},
    "en-IN": {"model": "timbre-v2.5", "voice": "Kaveri"},
}

FALLBACK_VOICE = {"model": "timbre-v3.0", "voice": "Chetana"}

