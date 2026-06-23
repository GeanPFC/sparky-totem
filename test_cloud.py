"""Buscar gemma-4 y probar con un modelo alternativo rapido."""

import requests
import json
import time
from sparky.config import CLOUD_API_KEY as API_KEY

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
headers_auth = {"Authorization": f"Bearer {API_KEY}"}

# Test 1: Buscar modelos gemma disponibles
print("=== Buscando modelos gemma ===")
resp = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers_auth, timeout=15)
models = resp.json().get("data", [])
gemma_models = [m["id"] for m in models if "gemma" in m["id"].lower()]
print(f"Modelos gemma encontrados ({len(gemma_models)}):")
for m in gemma_models:
    print(f"  - {m}")

# Buscar otros modelos buenos para espanol
print("\n=== Otros modelos interesantes ===")
good_models = [m["id"] for m in models if any(x in m["id"].lower() for x in ["llama", "qwen", "mistral"])]
for m in sorted(good_models)[:15]:
    print(f"  - {m}")

# Test 2: Probar con un modelo mas ligero (meta/llama)
test_models = [
    "google/gemma-3-27b-it",
    "meta/llama-3.1-8b-instruct",
]

for model_name in test_models:
    if model_name not in [m["id"] for m in models]:
        print(f"\n{model_name} -> NO disponible")
        continue

    print(f"\n=== Probando: {model_name} ===")
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "di hola en una sola palabra"}],
        "max_tokens": 20,
        "temperature": 0.7,
        "stream": True,
    }
    headers = {**headers_auth, "Accept": "text/event-stream"}

    start = time.time()
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=(10, 30))
        if resp.status_code != 200:
            print(f"  Error HTTP {resp.status_code}: {resp.text[:200]}")
            continue

        full = ""
        for line in resp.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data = line_str[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        full += content
                except:
                    pass

        elapsed = round(time.time() - start, 2)
        print(f"\n  Respuesta en {elapsed}s: '{full}'")
    except requests.exceptions.Timeout:
        elapsed = round(time.time() - start, 2)
        print(f"  TIMEOUT en {elapsed}s")
    except Exception as e:
        print(f"  ERROR: {e}")
