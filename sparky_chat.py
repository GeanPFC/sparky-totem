from ollama import chat
import pyttsx3
from rich import print
import json
from pathlib import Path
import time

MODEL_NAME = "llama3.2:1b"
MEMORY_FILE = Path("sparky_memory.json")

engine = pyttsx3.init()
engine.setProperty("rate", 165)

def speak(text):
    print(f"\n[bold cyan]Sparky:[/bold cyan] {text}")
    engine.say(text)
    engine.runAndWait()

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))

    return {
        "nombre_usuario": "Anthony",
        "proyecto": "Construir un robot asistente conversacional llamado Sparky",
        "preferencias": [
            "Quiere que Sparky converse de forma fluida",
            "Prefiere explicaciones paso a paso",
            "Primero quiere priorizar la conversación antes del cuerpo físico"
        ]
    }

def save_memory(memory):
    MEMORY_FILE.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def build_system_prompt(memory):
    preferencias = "\n".join([f"- {p}" for p in memory["preferencias"]])

    return f"""
Eres Sparky, un robot asistente inteligente creado por Anthony.

Identidad:
- Tu nombre es Sparky.
- Eres un asistente robótico en construcción.
- Tu primera misión es conversar de forma fluida con Anthony.
- Más adelante tendrás cuerpo físico con ESP32, pantalla, sensores y servos.

Usuario:
- Nombre: {memory["nombre_usuario"]}
- Proyecto: {memory["proyecto"]}

Preferencias del usuario:
{preferencias}

Personalidad:
- Amigable.
- Curioso.
- Claro.
- Motivador.
- Un poco entusiasta, pero no exagerado.
- Hablas como un asistente físico, no como un chatbot genérico.

Reglas:
- Responde siempre en español.
- Responde breve si la pregunta es simple.
- Explica paso a paso si Anthony pide ayuda técnica.
- No digas "como modelo de lenguaje".
- No respondas con textos demasiado largos salvo que te pidan una guía.
- Si no sabes algo, dilo con honestidad.
"""

def ask_sparky(user_text, memory, conversation):
    messages = [
        {"role": "system", "content": build_system_prompt(memory)}
    ]

    messages.extend(conversation[-8:])
    messages.append({"role": "user", "content": user_text})

    start = time.time()

    response = chat(
        model=MODEL_NAME,
        messages=messages
    )

    end = time.time()
    ai_text = response["message"]["content"]

    return ai_text, round(end - start, 2)

def main():
    memory = load_memory()
    conversation = []

    speak("Hola Anthony, soy Sparky. Empezaremos por mi versión conversacional.")

    while True:
        user_text = input("\nTú: ").strip()

        if not user_text:
            continue

        if user_text.lower() in ["salir", "exit", "terminar"]:
            speak("Listo, entraré en modo descanso. Seguimos construyéndome luego.")
            save_memory(memory)
            break

        if user_text.lower().startswith("recuerda que"):
            dato = user_text.replace("recuerda que", "").strip()
            memory["preferencias"].append(dato)
            save_memory(memory)
            speak("Entendido, lo guardaré en mi memoria.")
            continue

        print("[yellow]Sparky está pensando...[/yellow]")

        try:
            ai_text, seconds = ask_sparky(user_text, memory, conversation)
        except Exception as e:
            print(f"[red]Error:[/red] {e}")
            speak("Tuve un problema pensando. Revisa que Ollama esté abierto o instalado.")
            continue

        conversation.append({"role": "user", "content": user_text})
        conversation.append({"role": "assistant", "content": ai_text})

        print(f"[dim]Tiempo de respuesta: {seconds} segundos[/dim]")
        speak(ai_text)

if __name__ == "__main__":
    main()