"""
Módulo de escucha de Sparky — RealtimeSTT con auto-recuperación.

RealtimeSTT maneja internamente:
- VAD (Silero VAD + webrtcvad) en proceso separado
- Micrófono siempre activo (incluso durante TTS = barge-in)
- Transcripción con faster-whisper

Auto-recuperación:
- Si el proceso hijo muere (BrokenPipeError), se recrea automáticamente.
- Suprime los logs de error repetitivos del pipe roto.
"""

import logging
import time
from rich import print as rprint
from sparky.config import STT_MODEL, STT_LANGUAGE, BARGE_IN


class SparkyListener:
    """Escucha con RealtimeSTT + auto-recuperación ante crashes."""

    def __init__(self):
        self._recorder = None
        self._voice = None
        self._create_count = 0

    def set_voice(self, voice):
        """Conecta el módulo de voz para barge-in."""
        self._voice = voice

    def _on_recording_start(self):
        """Callback: se dispara cuando el usuario empieza a hablar.
        Si Sparky está hablando, lo para (barge-in).
        """
        if BARGE_IN and self._voice and self._voice.is_speaking:
            rprint("\n[bold red]⚡ Interrumpido![/bold red]")
            self._voice.stop_speaking()

    def _on_recording_stop(self):
        """Callback: el usuario dejó de hablar."""
        rprint("[dim]Procesando...[/dim]")

    def _create_recorder(self):
        """Crea (o recrea) el AudioToTextRecorder."""
        # Limpiar recorder anterior si existe
        if self._recorder is not None:
            try:
                self._recorder.shutdown()
            except Exception:
                pass
            self._recorder = None
            time.sleep(0.5)  # Dar tiempo a que el proceso hijo muera

        self._create_count += 1
        if self._create_count == 1:
            rprint("[yellow]Iniciando sistema de escucha...[/yellow]")
        else:
            rprint(f"[yellow]Reiniciando sistema de escucha (intento {self._create_count})...[/yellow]")

        # Suprimir los logs de error del pipe roto de RealtimeSTT
        logging.getLogger("root").setLevel(logging.CRITICAL)
        logging.getLogger().setLevel(logging.CRITICAL)

        from RealtimeSTT import AudioToTextRecorder

        self._recorder = AudioToTextRecorder(
            model=STT_MODEL,
            language=STT_LANGUAGE,
            compute_type="int8",
            device="cpu",

            # VAD settings
            silero_sensitivity=0.4,
            webrtc_sensitivity=3,
            post_speech_silence_duration=0.4,  # ponytail: 0.4 = mas agil; sube a 0.6 si corta frases
            min_length_of_recording=0.3,
            min_gap_between_recordings=0.1,

            # Callbacks para barge-in (vad_detect_start dispara al instante de oír voz)
            on_vad_detect_start=self._on_recording_start,
            on_recording_start=self._on_recording_start,
            on_recording_stop=self._on_recording_stop,

            # Sin wake word
            wake_words="",

            # Feedback
            spinner=False,
            use_microphone=True,

            # Performance
            beam_size=2,
            initial_prompt=None,
            suppress_tokens=[-1],
        )
        rprint("[green]Sistema de escucha listo.[/green]")

    def _ensure_recorder(self):
        """Inicializa el recorder si no existe."""
        if self._recorder is None:
            self._create_recorder()

    def listen_keyboard(self):
        """Espera texto del teclado."""
        try:
            text = input("\nTu (Enter = mic): ").strip()
            return text if text else None
        except (EOFError, KeyboardInterrupt):
            return "salir"

    def listen_vad(self):
        """Escucha con VAD (RealtimeSTT) + auto-recuperación.

        Si el proceso hijo crashea (BrokenPipeError), recrea el recorder
        automáticamente y vuelve a escuchar.
        """
        self._ensure_recorder()

        # Vaciar lo captado durante el turno anterior (ej. la propia voz de
        # Sparky por el altavoz). Conversación por turnos = sin eco.
        try:
            self._recorder.clear_audio_queue()
        except Exception:
            pass

        rprint("[bold green]🎤 Escuchando...[/bold green]")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                text = self._recorder.text()

                if text and text.strip():
                    rprint(f"[dim cyan]Escuché: \"{text.strip()}\"[/dim cyan]")
                    return text.strip()
                else:
                    return ""

            except BrokenPipeError:
                rprint(f"[yellow]Conexión perdida, reiniciando...[/yellow]")
                self._create_recorder()
                continue

            except OSError as e:
                if "WinError 109" in str(e) or "canalización" in str(e):
                    rprint(f"[yellow]Pipe roto, reiniciando...[/yellow]")
                    self._create_recorder()
                    continue
                else:
                    rprint(f"[red]Error OS: {e}[/red]")
                    return ""

            except Exception as e:
                error_str = str(e).lower()
                if "pipe" in error_str or "broken" in error_str or "109" in error_str:
                    rprint(f"[yellow]Error de conexión, reiniciando...[/yellow]")
                    self._create_recorder()
                    continue
                else:
                    rprint(f"[red]Error escuchando: {e}[/red]")
                    return ""

        rprint("[red]No se pudo recuperar después de varios intentos.[/red]")
        return ""

    def shutdown(self):
        """Cierra el recorder limpiamente."""
        if self._recorder:
            try:
                self._recorder.shutdown()
            except Exception:
                pass
            self._recorder = None
