"""
Avatar visual de Sparky — cara animada en el navegador (pantalla vertical).

Sirve una página full-screen con una cara que:
- mueve la boca cuando Sparky habla  (voice.is_speaking)
- cambia de expresión según la emoción (brain.last_emotion)

Arquitectura perezosa: http.server de la stdlib → CERO dependencias nuevas.
El navegador consulta /state cada ~120 ms; la animación de la boca es CSS en
el cliente, así que no necesita sincronía fina con el audio (como hacen los
avatares reales).
"""

import json
import time
import shutil
import threading
import webbrowser
import subprocess
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from rich import print as rprint
from sparky.config import (
    AVATAR_ENABLED, AVATAR_PORT, AVATAR_KIOSK, AVATAR_3D, SPARKY_NAME, TTS_ENGINE,
)

_LOG_FILE = Path(__file__).parent.parent / "avatar.log"

_HTML = (Path(__file__).parent / "avatar.html").read_text(encoding="utf-8")
_HTML_3D = (Path(__file__).parent / "avatar3d.html").read_text(encoding="utf-8")

# Rutas típicas de Chrome en Windows para el modo kiosko
_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


class SparkyAvatar:
    """Cara animada de Sparky servida por un http.server local."""

    def __init__(self, voice=None, brain=None):
        self.voice = voice
        self.brain = brain
        self._server = None

        # Cola de audio para reproducir en el navegador (modo 3D)
        self._audio = []                 # [{id, data(bytes)}] aún no servidos al navegador
        self._gen = 0                    # generación: sube en barge-in para cancelar
        self._next_id = 0
        self._audio_lock = threading.Lock()

    # ── Cola de audio (navegador reproduce → HeadAudio lip-sync) ──

    def push_audio(self, wav_bytes, visemes=None):
        """Encola un WAV (+ visemas opcionales) para el navegador. Devuelve su id."""
        with self._audio_lock:
            cid = self._next_id
            self._next_id += 1
            self._audio.append({"id": cid, "data": wav_bytes, "visemes": visemes})
            return cid

    def cancel_audio(self):
        """Barge-in: cancela todo lo pendiente y avisa al navegador (sube gen)."""
        with self._audio_lock:
            self._gen += 1
            self._audio.clear()

    def take_audio(self, cid):
        """El navegador descarga un clip (dict con data+visemas): se entrega una vez."""
        with self._audio_lock:
            for i, c in enumerate(self._audio):
                if c["id"] == cid:
                    return self._audio.pop(i)
        return None

    def _state(self):
        emotion = (self.brain.last_emotion if self.brain else "neutral") or "neutral"
        speaking = bool(self.voice and self.voice.is_speaking)
        with self._audio_lock:
            pending = [{"id": c["id"], "url": f"/audio/{c['id']}"} for c in self._audio]
            gen = self._gen
        return {"speaking": speaking, "emotion": emotion, "name": SPARKY_NAME,
                "gen": gen, "audio": pending, "tts": TTS_ENGINE}

    def start(self):
        if not AVATAR_ENABLED:
            return
        avatar = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass  # silenciar logs HTTP

            def do_GET(self):
              try:
                if self.path.startswith("/log"):
                    msg = parse_qs(urlparse(self.path).query).get("m", [""])[0]
                    line = "[" + time.strftime("%H:%M:%S") + "] navegador: " + msg
                    try:
                        with open(_LOG_FILE, "a", encoding="utf-8") as f:
                            f.write(line + "\n")
                    except OSError:
                        pass
                    # print plano y ascii-safe (rich/cp1252 en Windows revientan con emojis)
                    try:
                        print(line.encode("ascii", "replace").decode("ascii"), flush=True)
                    except Exception:
                        pass
                    body = b"ok"
                    ctype = "text/plain"
                elif self.path.startswith("/audio/"):
                    try:
                        cid = int(self.path.rsplit("/", 1)[1].split("?")[0])
                    except ValueError:
                        cid = -1
                    clip = avatar.take_audio(cid)
                    if clip is None:
                        self.send_error(404, "audio no disponible")
                        return
                    import base64
                    payload = {"audio": base64.b64encode(clip["data"]).decode("ascii")}
                    if clip.get("visemes"):
                        payload.update(clip["visemes"])  # visemes, vtimes, vdurations
                    body = json.dumps(payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(body)
                    return
                elif self.path.startswith("/state"):
                    body = json.dumps(avatar._state()).encode("utf-8")
                    ctype = "application/json"
                elif self.path.startswith("/3d"):
                    body = _HTML_3D.encode("utf-8")
                    ctype = "text/html; charset=utf-8"
                else:
                    body = _HTML.encode("utf-8")
                    ctype = "text/html; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
              except Exception as e:
                try:
                    self.send_error(500, str(e))
                except Exception:
                    pass

        # En Windows, SO_REUSEADDR deja que DOS servidores tomen el mismo puerto
        # y el navegador se engancha al fantasma. Lo desactivamos para fallar claro.
        ThreadingHTTPServer.allow_reuse_address = False
        try:
            self._server = ThreadingHTTPServer(("127.0.0.1", AVATAR_PORT), Handler)
        except OSError:
            rprint(f"[bold red]Puerto {AVATAR_PORT} ya ocupado por otro Sparky.[/bold red]")
            rprint("[yellow]Cierra los 'python' viejos (Administrador de tareas) y reinicia.[/yellow]")
            return
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

        url = f"http://127.0.0.1:{AVATAR_PORT}/" + ("3d" if AVATAR_3D else "")
        rprint(f"[dim]Avatar: {url}[/dim]")
        self._open_browser(url)

    def _open_browser(self, url):
        """Abre Chrome en modo kiosko si se puede; si no, el navegador por defecto."""
        if AVATAR_KIOSK:
            chrome = shutil.which("chrome") or next(
                (p for p in _CHROME_PATHS if Path(p).exists()), None
            )
            if chrome:
                try:
                    subprocess.Popen([chrome, "--kiosk", "--noerrdialogs",
                                      "--disable-infobars",
                                      "--autoplay-policy=no-user-gesture-required", url])
                    return
                except Exception:
                    pass
        webbrowser.open(url)  # fallback: pestaña normal (pulsa F11 para pantalla completa)

    def shutdown(self):
        if self._server is not None:
            try:
                self._server.shutdown()
            except Exception:
                pass
            self._server = None
