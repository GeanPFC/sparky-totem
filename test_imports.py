"""Test de imports para Sparky v3.0"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("--- Sparky v3.0 Import Test ---\n")

tests = [
    ("config", "from sparky.config import WAKE_WORD_ENABLED, VAD_ENERGY_THRESHOLD"),
    ("emotions", "from sparky.emotions import parse_emotion"),
    ("memory", "from sparky.memory import SparkyMemory"),
    ("brain", "from sparky.brain import SparkyBrain"),
    ("voice", "from sparky.voice import SparkyVoice"),
    ("listener", "from sparky.listener import SparkyListener"),
    ("sounddevice", "import sounddevice"),
    ("numpy", "import numpy"),
    ("faster_whisper", "import faster_whisper"),
    ("openwakeword", "import openwakeword"),
    ("requests", "import requests"),
]

all_ok = True
for name, imp in tests:
    try:
        exec(imp)
        print(f"  [OK] {name}")
    except Exception as e:
        print(f"  [FALLO] {name}: {e}")
        all_ok = False

print(f"\n{'Todos los imports OK' if all_ok else 'HAY FALLOS'}")
print("--- Listo ---")
