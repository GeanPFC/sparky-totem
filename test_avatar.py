"""Previsualiza el avatar: abre la cara y la hace ciclar por todas las
emociones y el estado 'hablando', sin necesidad de micrófono ni LLM.

Uso:  venv\\Scripts\\python.exe test_avatar.py   (Ctrl+C para salir)
"""

import time
import sparky.avatar as av

av.AVATAR_KIOSK = False  # pestaña normal para la previsualización (no kiosko)


class FakeVoice:
    is_speaking = False

class FakeBrain:
    last_emotion = "neutral"


voice, brain = FakeVoice(), FakeBrain()
avatar = av.SparkyAvatar(voice, brain)
avatar.start()

emociones = ["neutral", "happy", "thinking", "sad", "alert", "sleep"]
print("Mira el navegador. Ciclando emociones (Ctrl+C para salir)...\n")

try:
    while True:
        for emo in emociones:
            brain.last_emotion = emo
            # Habla un par de segundos en cada emoción, luego escucha
            voice.is_speaking = True
            print(f"  {emo} + hablando")
            time.sleep(2.5)
            voice.is_speaking = False
            print(f"  {emo} + en silencio")
            time.sleep(1.5)
except KeyboardInterrupt:
    print("\nFin de la previsualización.")
    avatar.shutdown()
