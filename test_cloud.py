"""Diagnóstico del LLM en la nube (NVIDIA). Dice si tu clave sirve para chat.

Uso:  venv\\Scripts\\python test_cloud.py
"""

import requests
from sparky.config import CLOUD_API_KEY, CLOUD_API_URL, CLOUD_MODEL

print("Clave :", (CLOUD_API_KEY[:14] + "...") if CLOUD_API_KEY else "(VACÍA)")
print("URL   :", CLOUD_API_URL)
print("Modelo:", CLOUD_MODEL)
print("-" * 50)

try:
    r = requests.post(
        CLOUD_API_URL,
        headers={"Authorization": f"Bearer {CLOUD_API_KEY}", "Accept": "application/json"},
        json={"model": CLOUD_MODEL,
              "messages": [{"role": "user", "content": "di hola en una palabra"}],
              "max_tokens": 10},
        timeout=20,
    )
    print("HTTP", r.status_code)
    if r.status_code == 200:
        print("Respuesta:", r.json()["choices"][0]["message"]["content"].strip())
        print("\n>>> LLM OK: la clave sirve. El problema está en otro lado.")
    else:
        print("Cuerpo del error:", r.text[:500])
        print("\n>>> La clave NO funciona para este modelo. Causas típicas:")
        print("    401 = clave inválida | 403 = sin acceso al modelo | 404 = modelo mal escrito")
except Exception as e:
    print("EXCEPCIÓN:", repr(e))
    print("\n>>> No se pudo conectar (red/SSL/proxy).")
