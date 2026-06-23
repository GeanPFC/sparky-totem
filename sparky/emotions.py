"""
Sistema de emociones de Sparky.

Cada respuesta de Sparky incluye una emoción detectada del texto.
El modelo prefija su respuesta con [emocion] y este módulo lo parsea.

Emociones disponibles:
    neutral, happy, thinking, sad, alert, sleep
"""

# Mapa de emociones → emoji + color Rich para la terminal
EMOTIONS = {
    "neutral":  {"emoji": "😐", "color": "white",   "label": "Neutral"},
    "happy":    {"emoji": "😊", "color": "green",   "label": "Contento"},
    "thinking": {"emoji": "🤔", "color": "yellow",  "label": "Pensando"},
    "sad":      {"emoji": "😔", "color": "blue",    "label": "Triste"},
    "alert":    {"emoji": "⚡", "color": "red",     "label": "Alerta"},
    "sleep":    {"emoji": "😴", "color": "dim",     "label": "Dormido"},
}

DEFAULT_EMOTION = "neutral"


def parse_emotion(text):
    """Extrae la etiqueta de emoción del inicio del texto.

    Espera formato: [happy] Hola Anthony!
    Retorna: ("happy", "Hola Anthony!")

    Si no hay etiqueta, retorna: ("neutral", texto_original)
    """
    text = text.strip()

    if text.startswith("["):
        bracket_end = text.find("]")
        if bracket_end != -1 and bracket_end < 20:  # Máx 20 chars para la etiqueta
            emotion_tag = text[1:bracket_end].strip().lower()
            clean_text = text[bracket_end + 1:].strip()

            if emotion_tag in EMOTIONS:
                return emotion_tag, clean_text

    return DEFAULT_EMOTION, text


def format_emotion(emotion):
    """Retorna string formateado con emoji y label para mostrar en terminal."""
    info = EMOTIONS.get(emotion, EMOTIONS[DEFAULT_EMOTION])
    return f"{info['emoji']} {info['label']}"


def get_emotion_color(emotion):
    """Retorna el color Rich para una emoción."""
    info = EMOTIONS.get(emotion, EMOTIONS[DEFAULT_EMOTION])
    return info["color"]
