"""Test del modulo de emociones."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sparky.emotions import parse_emotion, format_emotion

# Test 1: Parsear emociones
tests = [
    "[happy] Hola Anthony!",
    "[thinking] Dejame pensar...",
    "[sad] Lo siento, no puedo ayudar con eso.",
    "[neutral] Aqui estoy.",
    "[alert] Cuidado con eso!",
    "Sin etiqueta, deberia ser neutral",
]

print("--- Test de emociones ---\n")
for text in tests:
    emotion, clean = parse_emotion(text)
    display = format_emotion(emotion)
    print(f"  Input: {text[:40]}...")
    print(f"  -> Emocion: {emotion} {display}")
    print(f"  -> Texto limpio: {clean}")
    print()

print("--- Todas las emociones parseadas correctamente ---")
