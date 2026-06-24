"""
Configuración centralizada de Sparky.
Cambia estos valores para ajustar el comportamiento sin tocar otros módulos.
"""

import os
from pathlib import Path

# ── Modelo LOCAL (Ollama) ─────────────────────────────────────
LOCAL_MODEL = "llama3.2:1b"
LOCAL_OPTIONS = {
    "num_predict": 150,
    "num_ctx": 2048,
    "temperature": 0.7,
}

# ── Modelo en NUBE (NVIDIA API) ───────────────────────────────
CLOUD_ENABLED = True
CLOUD_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# La clave se lee de sparky/secrets.py (no versionado) o de la variable de entorno
try:
    from sparky.secrets import NVIDIA_API_KEY as CLOUD_API_KEY
except ImportError:
    CLOUD_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
CLOUD_MODEL = "meta/llama-3.1-8b-instruct"
CLOUD_MAX_TOKENS = 200
CLOUD_TEMPERATURE = 0.7
CLOUD_TIMEOUT = 20                  # el endpoint gratis a veces tarda en el 1er token; 5s era muy corto

# ── Conversación ──────────────────────────────────────────────
MAX_HISTORY_MESSAGES = 4

# ── Memoria ───────────────────────────────────────────────────
MEMORY_FILE = Path(__file__).parent.parent / "sparky_memory.json"

# ── Voz (Piper TTS) ──────────────────────────────────────────
VOICE_ENABLED = True
PIPER_EXE = Path(__file__).parent.parent / "piper" / "piper" / "piper.exe"
PIPER_MODEL = Path(__file__).parent.parent / "piper" / "piper" / "es_MX-ald-medium.onnx"
PIPER_SAMPLE_RATE = 22050
PIPER_SENTENCE_SILENCE = 0.15       # Silencio tras cada frase (default piper: 0.2)
PIPER_TMP = Path(__file__).parent.parent / "tmp_tts"  # WAVs temporales del proceso caliente
VOICE_RATE = 165                    # Velocidad pyttsx3 (fallback)

# ── Filler (muletilla para tapar la latencia del LLM) ────────
FILLER_ENABLED = True
FILLER_PHRASES = ["Mmm,", "A ver,", "Déjame ver,"]

# ── Chatterbox TTS (NVIDIA Riva gRPC) ────────────────────────
TTS_ENGINE = "piper"               # "piper" (local, gratis) | "riva" (Chatterbox; requiere function-id habilitado en tu cuenta)
RIVA_SERVER = "grpc.nvcf.nvidia.com:443"
RIVA_FUNCTION_ID = "ddacc747-1269-4fab-bfd9-8f593dead106"  # chatterbox-multilingual-tts
RIVA_VOICE = "Chatterbox-Multilingual.es-US.Female"  # conjetura; confirma el real con list_voices.py
RIVA_LANGUAGE = "es-US"               # el español en Chatterbox/NVIDIA es es-US
RIVA_SAMPLE_RATE = 22050

# ── STT (RealtimeSTT + faster-whisper) ───────────────────────
STT_MODEL = "base"                  # tiny=rápido, base=equilibrado, small=preciso
STT_LANGUAGE = "es"

# ── Avatar visual (cara en pantalla vertical) ────────────────
AVATAR_ENABLED = True
AVATAR_PORT = 8730
AVATAR_KIOSK = True                 # abrir Chrome en modo kiosko (pantalla completa)
AVATAR_3D = True                    # True: avatar humano 3D (/3d, audio en navegador); False: cara 2D
TOTEM_MODE = True                   # True: escucha sola por micrófono (sin pulsar Enter)
BARGE_IN = False                    # ponytail: False evita autointerrupción por eco de altavoz.
                                    # Ponlo True solo con auriculares o micrófono con cancelación de eco.

# ── Identidad de Sparky ───────────────────────────────────────
SPARKY_NAME = "Sparky"
CREATOR_NAME = "Anthony"
