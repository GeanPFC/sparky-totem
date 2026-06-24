"""Prueba el CEREBRO solo (sin micrófono ni avatar). Debe imprimir respuestas.

Uso:  venv\\Scripts\\python test_brain.py
Si responde → el "problema pensando" está resuelto y main.py funcionará.
"""

from sparky.brain import SparkyBrain
from sparky.memory import SparkyMemory

brain, mem = SparkyBrain(), SparkyMemory()
preguntas = ["hola, ¿quién eres?", "¿qué puedes hacer por mí?"]

ok = True
for q in preguntas:
    print(f"\n>> Tú: {q}")
    resp, secs = brain.think(q, mem.build_system_prompt(), voice=None)
    print(f"\n[motor: {brain.last_engine} | {secs}s] Sparky: {resp}")
    if resp is None:
        print(">>> FALLO: 'problema pensando'")
        ok = False
        break

print("\n>>> CEREBRO OK ✅ — main.py responderá" if ok else "\n>>> Revisa el error de arriba")
