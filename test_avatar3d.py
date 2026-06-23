"""Prueba del Hito 2: el avatar 3D habla con la voz de Piper y mueve los labios.

No necesita micrófono, LLM ni tocar la consola. Arranca el servidor y, en bucle,
hace que el avatar diga unas frases en español. Solo tienes que abrir el navegador.

Uso:
    venv\\Scripts\\python.exe test_avatar3d.py
    → abre http://127.0.0.1:8730/3d   (el avatar carga y habla solo cada pocos segundos)
    Ctrl+C para salir.
"""

import time
import threading
from sparky.voice import SparkyVoice
from sparky.avatar import SparkyAvatar


class FakeBrain:
    last_emotion = "happy"


voice = SparkyVoice()
avatar = SparkyAvatar(voice, FakeBrain())
voice.set_avatar(avatar)
avatar.start()

print("\n>>> Abre http://127.0.0.1:8730/3d  (el avatar hablará solo cada ~6 s)")
print(">>> Ctrl+C para salir.\n")

frases = [
    "Hola, soy Sparky, tu asistente virtual.",
    "Hablo con voz natural y mis labios se mueven con el audio.",
    "Encantado de conocerte. ¿En qué puedo ayudarte?",
]

try:
    while True:
        time.sleep(6)
        print("Sparky habla…")
        voice.start_speaking()
        for f in frases:
            voice.queue_sentence(f)
        voice.finish_speaking()
except KeyboardInterrupt:
    print("\nSaliendo…")
    voice.shutdown()
    avatar.shutdown()
