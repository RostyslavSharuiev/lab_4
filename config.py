"""Configuration models for Text-to-Speech (TTS) synthesis and audio output."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class VoiceConfig:
    """Configuration settings for voice selection.

    Attributes:
        language: Language keyword or locale code to search for (e.g., 'english', 'en', 'ru').
        voice_id: Exact voice identifier string (overrides language matching if provided).
    """

    language: str = "english"
    voice_id: str | None = None

    def __post_init__(self) -> None:
        """Validate voice configuration parameters."""
        if not self.voice_id and not self.language.strip():
            raise ValueError("Either a non-empty voice language or a voice ID must be provided.")


@dataclass(frozen=True)
class SpeechConfig:
    """Configuration settings for speech generation and playback.

    Attributes:
        text: Text to be synthesized into speech.
        rate: Speech speed rate in words per minute (e.g., 150).
        volume: Speech volume level between 0.0 (silent) and 1.0 (full volume).
        play: Whether to play synthesized audio through the system speakers.
        voice: Voice selection configuration model.
    """

    text: str = "Hello! This is local speech synthesis running completely offline without external servers."
    rate: int = 150
    volume: float = 1.0
    play: bool = True
    voice: VoiceConfig = field(default_factory=VoiceConfig)

    def __post_init__(self) -> None:
        """Validate speech configuration parameters."""
        if self.rate <= 0:
            raise ValueError(f"Speech rate must be positive, got {self.rate}")

        if not 0.0 <= self.volume <= 1.0:
            raise ValueError(f"Speech volume must be between 0.0 and 1.0, got {self.volume}")

        if not self.text.strip():
            raise ValueError("Speech text cannot be empty or whitespace only.")


@dataclass(frozen=True)
class OutputConfig:
    """Configuration settings for audio file persistence.

    Attributes:
        save: Whether to save synthesized speech to an audio file on disk.
        output_dir: Directory where the generated audio file will be saved.
        output_filename: Name of the output audio file without extension.
        output_extension: Container format / extension (default: 'wav').
    """

    save: bool = True
    output_dir: Path = field(default_factory=lambda: Path("output"))
    output_filename: str = "output"
    output_extension: str = "wav"

    def __post_init__(self) -> None:
        """Validate output configuration parameters and normalize extension."""
        if not self.output_filename.strip():
            raise ValueError("Output filename cannot be empty.")

        cleaned_ext = self.output_extension.lstrip(".")
        if not cleaned_ext:
            raise ValueError("Output extension cannot be empty.")

        object.__setattr__(self, "output_extension", cleaned_ext)

    @property
    def file_path(self) -> Path:
        """Return the fully resolved target file path for the audio output."""
        return self.output_dir / f"{self.output_filename}.{self.output_extension}"

    def file_path_with_suffix(self, suffix: str) -> Path:
        """Return output file path with an appended filename suffix."""
        return self.output_dir / f"{self.output_filename}{suffix}.{self.output_extension}"


@dataclass(frozen=True)
class AppConfig:
    """Aggregate configuration holding all application domain configs.

    Attributes:
        speech: Speech synthesis and playback configuration.
        output: Audio file destination and saving configuration.
        list_voices: Flag to list available system voices and exit without synthesizing.
        verbose: Enable debug logging verbosity.
    """

    speech: SpeechConfig
    output: OutputConfig
    list_voices: bool = False
    verbose: bool = False

    def __post_init__(self) -> None:
        """Ensure valid action combination if not merely querying voices."""
        if not self.list_voices and not self.speech.play and not self.output.save:
            raise ValueError("At least one action (speaker playback or file saving) must be enabled.")
