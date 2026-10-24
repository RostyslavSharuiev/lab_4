"""Command Line Interface (CLI) module for parsing text-to-speech application arguments."""

import argparse
from pathlib import Path

from config import AppConfig, OutputConfig, SpeechConfig, VoiceConfig


def parse_args(args: None | list[str] = None) -> AppConfig:
    """Parse command line arguments and return a validated AppConfig instance.

    Args:
        args: Optional list of command-line argument strings (useful for programmatic invocation and testing).

    Returns:
        AppConfig: Aggregate configuration object holding validated domain configurations.
    """
    default_speech = SpeechConfig()
    default_voice = default_speech.voice
    default_output = OutputConfig()

    parser = argparse.ArgumentParser(
        prog="tts-synthesizer",
        description="Production-grade command-line utility for local Text-to-Speech (TTS) synthesis.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Speech generation group
    speech_group = parser.add_argument_group("Speech Settings")
    speech_group.add_argument(
        "-t",
        "--text",
        type=str,
        default=default_speech.text,
        dest="text",
        help="Text to synthesize into speech",
    )
    speech_group.add_argument(
        "-r",
        "--rate",
        type=int,
        default=default_speech.rate,
        dest="rate",
        help="Speech speed rate in words per minute",
    )
    speech_group.add_argument(
        "-v",
        "--volume",
        type=float,
        default=default_speech.volume,
        dest="volume",
        help="Speech volume level (0.0 to 1.0)",
    )
    speech_group.add_argument(
        "-l",
        "--lang",
        type=str,
        default=default_voice.language,
        dest="language",
        help="Target language keyword or code (e.g., 'english', 'en', 'ru')",
    )
    speech_group.add_argument(
        "--voice-id",
        type=str,
        default=default_voice.voice_id,
        dest="voice_id",
        help="Explicit system voice ID or token to use",
    )

    # Output file settings group
    output_group = parser.add_argument_group("Output File Settings")
    output_group.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=default_output.output_dir,
        dest="output_dir",
        help="Directory where synthesized audio file will be written",
    )
    output_group.add_argument(
        "-n",
        "--name",
        type=str,
        default=default_output.output_filename,
        dest="output_filename",
        help="Output audio filename (without extension)",
    )
    output_group.add_argument(
        "-e",
        "--ext",
        type=str,
        default=default_output.output_extension,
        dest="output_extension",
        help="Audio container file extension (e.g., 'wav')",
    )
    output_group.add_argument(
        "--no-save",
        action="store_false",
        dest="save",
        default=default_output.save,
        help="Disable saving synthesized audio to disk",
    )

    # Playback settings group
    playback_group = parser.add_argument_group("Playback Settings")
    playback_group.add_argument(
        "--no-play",
        action="store_false",
        dest="play",
        default=default_speech.play,
        help="Disable real-time audio playback through system speakers",
    )

    # Utility options
    util_group = parser.add_argument_group("Utility Options")
    util_group.add_argument(
        "--list-voices",
        action="store_true",
        dest="list_voices",
        default=False,
        help="List all available system voices and exit",
    )
    util_group.add_argument(
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Enable verbose debug log messages",
    )

    parsed = parser.parse_args(args)

    voice_config = VoiceConfig(
        language=parsed.language,
        voice_id=parsed.voice_id,
    )

    speech_config = SpeechConfig(
        text=parsed.text,
        rate=parsed.rate,
        volume=parsed.volume,
        play=parsed.play,
        voice=voice_config,
    )

    output_config = OutputConfig(
        save=parsed.save,
        output_dir=parsed.output_dir,
        output_filename=parsed.output_filename,
        output_extension=parsed.output_extension,
    )

    return AppConfig(
        speech=speech_config,
        output=output_config,
        list_voices=parsed.list_voices,
        verbose=parsed.verbose,
    )
