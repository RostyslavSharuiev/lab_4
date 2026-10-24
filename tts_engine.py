"""Text-to-Speech (TTS) engine interfaces and pyttsx3 implementation."""

import logging
from pathlib import Path
from typing import Any, Callable, Protocol

from voice_selector import VoiceInfo

logger = logging.getLogger(__name__)


# =====================================================================
# Domain Exceptions
# =====================================================================

class TTSError(Exception):
    """Base exception for all text-to-speech engine errors."""


class TTSInitializationError(TTSError):
    """Raised when the underlying speech engine fails to initialize."""



class SynthesisError(TTSError):
    """Raised when speech synthesis or playback fails."""


class AudioSaveError(TTSError):
    """Raised when writing the synthesized audio file to disk fails."""


# =====================================================================
# Segregated Interfaces (ISP & DIP)
# =====================================================================

class IVoiceProvider(Protocol):
    """Interface for discovering available system voices."""

    def get_voices(self) -> list[VoiceInfo]:
        """Query and return all available speech voices."""
        ...


class ISpeechSpeaker(Protocol):
    """Interface for direct speaker audio playback."""

    def speak(self, text: str) -> None:
        """Synthesize and immediately play speech through system audio output."""
        ...


class ISpeechSaver(Protocol):
    """Interface for saving synthesized speech to an audio file."""

    def save_to_file(self, text: str, target_path: Path) -> Path:
        """Synthesize speech and write output to the target file path."""
        ...


class ITTSEngine(IVoiceProvider, ISpeechSpeaker, ISpeechSaver, Protocol):
    """Unified text-to-speech contract combining discovery, configuration, and output."""

    def configure(self, rate: int, volume: float, voice_id: str | None = None) -> None:
        """Apply speech synthesis settings to the engine."""
        ...

    def synthesize(
        self,
        text: str,
        play: bool = True,
        save_path: Path | None = None,
    ) -> Path | None:
        """Synthesize speech with optional playback and/or file persistence."""
        ...


# =====================================================================
# Concrete Implementation: Pyttsx3 Engine
# =====================================================================

class Pyttsx3Engine:
    """Concrete TTS engine implementation utilizing the pyttsx3 local library.

    Args:
        init_fn: Optional factory function returning a pyttsx3 engine instance.
                 Defaults to pyttsx3.init.
    """

    def __init__(self, init_fn: Callable[[], Any] | None = None) -> None:
        self._init_fn = init_fn
        self._engine: Any = None

    def _get_engine(self) -> Any:
        """Lazy initialization of the pyttsx3 engine."""
        if self._engine is None:
            try:
                if self._init_fn is not None:
                    self._engine = self._init_fn()
                else:
                    import pyttsx3
                    self._engine = pyttsx3.init()
                logger.debug("Initialized pyttsx3 synthesis engine.")
            except Exception as err:
                logger.error("Failed to initialize pyttsx3 engine: %s", err)
                raise TTSInitializationError(f"Could not initialize pyttsx3 engine: {err}") from err
        return self._engine

    def get_voices(self) -> list[VoiceInfo]:
        """Retrieve and parse voices reported by the pyttsx3 backend.

        Returns:
            list[VoiceInfo]: Discovered voices with ID, name, and language codes.
        """
        engine = self._get_engine()
        try:
            raw_voices = engine.getProperty("voices") or []
            voices: list[VoiceInfo] = []
            for v in raw_voices:
                languages = getattr(v, "languages", []) or []
                clean_langs: list[str] = []
                for item in languages:
                    if isinstance(item, (bytes, bytearray)):
                        clean_langs.append(item.decode("utf-8", errors="ignore"))
                    else:
                        clean_langs.append(str(item))
                voices.append(
                    VoiceInfo(
                        id=str(getattr(v, "id", "")),
                        name=str(getattr(v, "name", "Unknown Voice")),
                        languages=clean_langs,
                    )
                )
            logger.debug("Discovered %d voices from pyttsx3 backend.", len(voices))
            return voices
        except Exception as err:
            logger.error("Failed to retrieve system voices: %s", err)
            raise TTSError(f"Error reading voices from engine: {err}") from err

    def configure(self, rate: int, volume: float, voice_id: str | None = None) -> None:
        """Apply speech rate, volume, and voice selection to the pyttsx3 engine.

        Args:
            rate: Speech rate in words per minute.
            volume: Speech volume between 0.0 and 1.0.
            voice_id: System voice token or identifier.
        """
        engine = self._get_engine()
        try:
            engine.setProperty("rate", rate)
            engine.setProperty("volume", volume)
            logger.debug("Configured rate=%d, volume=%.2f", rate, volume)

            if voice_id:
                engine.setProperty("voice", voice_id)
                logger.info("Active voice set to: %s", voice_id)
        except Exception as err:
            logger.error("Failed to configure pyttsx3 parameters: %s", err)
            raise TTSError(f"Failed to configure engine: {err}") from err

    def speak(self, text: str) -> None:
        """Speak the given text immediately using the system speakers.

        Args:
            text: Text to synthesize.

        Raises:
            SynthesisError: If playback fails.
        """
        engine = self._get_engine()
        logger.info("Speaking text via speakers: \"%s\"", text)
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as err:
            logger.error("Speech playback failed: %s", err)
            raise SynthesisError(f"Playback failed: {err}") from err

    def save_to_file(self, text: str, target_path: Path) -> Path:
        """Synthesize text and save the resulting audio file.

        Args:
            text: Text to synthesize.
            target_path: File path where audio should be saved.

        Returns:
            Path: Resolved absolute path to saved audio file.

        Raises:
            AudioSaveError: If saving the audio file fails.
        """
        engine = self._get_engine()
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Queueing speech synthesis to file: %s", target_path)
            engine.save_to_file(text, str(target_path))
            engine.runAndWait()

            resolved = target_path.resolve()
            logger.info("Audio successfully saved to: %s", resolved)
            return resolved
        except Exception as err:
            logger.error("Failed to save audio file to %s: %s", target_path, err)
            raise AudioSaveError(f"Failed to save audio file to {target_path}: {err}") from err

    def synthesize(
        self,
        text: str,
        play: bool = True,
        save_path: Path | None = None,
    ) -> Path | None:
        """Unified synthesis workflow executing playback, file saving, or both in a single pass.

        Args:
            text: Text to synthesize.
            play: If True, output speech through speakers.
            save_path: If provided, save speech to this file path.

        Returns:
            Path | None: Resolved audio file path if save_path was provided; None otherwise.
        """
        if not play and save_path is None:
            logger.warning("Neither playback nor file saving was requested.")
            return None

        engine = self._get_engine()
        saved_resolved: Path | None = None

        try:
            if play:
                logger.info("Queueing audio playback for: \"%s\"", text)
                engine.say(text)

            if save_path is not None:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info("Queueing audio file export to: %s", save_path)
                engine.save_to_file(text, str(save_path))
                saved_resolved = save_path.resolve()

            engine.runAndWait()

            if saved_resolved is not None:
                logger.info("Audio export completed: %s", saved_resolved)

            return saved_resolved
        except Exception as err:
            logger.error("Synthesis pipeline execution failed: %s", err)
            raise SynthesisError(f"Speech synthesis failed: {err}") from err


# =====================================================================
# Mock / Test Implementation (Demonstrates LSP & facilitates unit testing)
# =====================================================================

class MockTTSEngine:
    """Mock TTS engine for unit testing without audio hardware or native dependencies."""

    def __init__(self, voices: list[VoiceInfo] | None = None) -> None:
        self.voices = voices or [
            VoiceInfo(id="mock-ru", name="Mock Russian Voice", languages=["ru-RU"]),
            VoiceInfo(id="mock-en", name="Mock English Voice", languages=["en-US"]),
        ]
        self.spoken_texts: list[str] = []
        self.saved_files: list[tuple[str, Path]] = []
        self.current_rate: int = 150
        self.current_volume: float = 1.0
        self.current_voice_id: str | None = None

    def get_voices(self) -> list[VoiceInfo]:
        return list(self.voices)

    def configure(self, rate: int, volume: float, voice_id: str | None = None) -> None:
        self.current_rate = rate
        self.current_volume = volume
        self.current_voice_id = voice_id

    def speak(self, text: str) -> None:
        self.spoken_texts.append(text)

    def save_to_file(self, text: str, target_path: Path) -> Path:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(f"MOCK AUDIO: {text}", encoding="utf-8")
        self.saved_files.append((text, target_path))
        return target_path.resolve()

    def synthesize(
        self,
        text: str,
        play: bool = True,
        save_path: Path | None = None,
    ) -> Path | None:
        if play:
            self.speak(text)
        if save_path is not None:
            return self.save_to_file(text, save_path)
        return None
