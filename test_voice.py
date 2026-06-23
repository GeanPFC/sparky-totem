"""Auto-test de latencia de voz: el proceso Piper caliente debe sintetizar
las frases siguientes MUCHO mas rapido que recargando el modelo (~2 s).

Verifica el nucleo de la optimizacion sin depender de un dispositivo de audio:
mide el tiempo desde 'pedir sintesis' hasta 'WAV listo'.
"""

import time
from sparky.voice import SparkyVoice

voice = SparkyVoice(enabled=True)
assert voice.engine_name == "piper", "Piper no disponible; este test requiere Piper."

frases = [
    "Hola, soy Sparky, tu asistente.",
    "Esta es la segunda frase, ya en caliente.",
    "Y la tercera deberia ir igual de rapida.",
]

tiempos = []
for i, f in enumerate(frases, 1):
    t = time.time()
    path = voice._synth(f)
    assert voice._wait_ready(path), f"WAV de la frase {i} no se completo"
    dt = time.time() - t
    tiempos.append(dt)
    print(f"  frase {i}: lista en {dt:.3f}s")

# Las frases en caliente (2+) deben ser claramente mas rapidas que recargar
# el modelo, que costaba ~2 s. Margen amplio para CPUs lentas.
calientes = tiempos[1:]
assert all(t < 1.0 for t in calientes), f"Frases en caliente demasiado lentas: {calientes}"
print(f"\nOK: frases en caliente ~{sum(calientes)/len(calientes):.2f}s (antes ~2s c/u)")

voice.shutdown()
