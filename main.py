"""Main application entry point for the Text-to-Speech (TTS) Synthesizer CLI tool."""

import logging
import sys
from enum import IntEnum
from cli import parse_args
from config import AppConfig
from logger import setup_logging
from tts_engine import ITTSEngine, Pyttsx3Engine, TTSError
from voice_selector import DefaultVoiceSelector, IVoiceSelector


class ExitCode(IntEnum):
    """Standardized application exit codes."""

    SUCCESS = 0
    FAILURE = 1
    INVALID_CONFIG = 2
    INTERRUPTED = 130


def run_pipeline(
    config: AppConfig,
    engine: ITTSEngine | None = None,
    selector: IVoiceSelector | None = None,
) -> int:
    """Execute the text-to-speech processing pipeline according to the given configuration.

    Args:
        config: Application configuration object.
        engine: Optional TTS engine instance implementing ITTSEngine (defaults to Pyttsx3Engine).
        selector: Optional voice selector strategy implementing IVoiceSelector (defaults to DefaultVoiceSelector).

    Returns:
        int: Exit code representing outcome.
    """
    logger = logging.getLogger("main")
    engine = engine or Pyttsx3Engine()
    selector = selector or DefaultVoiceSelector()

    # 1. Handle voice listing mode
    if config.list_voices:
        voices = engine.get_voices()
        logger.info("Found %d installed system voices:", len(voices))

        for index, voice in enumerate(voices, start=1):
            langs = ", ".join(voice.languages) if voice.languages else "N/A"
            logger.info("  [%d] %s (ID: %s, Langs: [%s])", index, voice.name, voice.id, langs)

        return ExitCode.SUCCESS

    # 2. Query available voices and match requested configuration
    available_voices = engine.get_voices()
    selected_voice = selector.select_voice(available_voices, config.speech.voice)

    if selected_voice:
        logger.info("Using selected voice: %s (%s)", selected_voice.name, selected_voice.id)
    else:
        logger.info("Using system default voice (no custom match found).")

    # 3. Configure speech engine parameters
    engine.configure(
        rate=config.speech.rate,
        volume=config.speech.volume,
        voice_id=selected_voice.id if selected_voice else None,
    )

    # 4. Execute synthesis (playback and/or file export)
    target_path = config.output.file_path if config.output.save else None

    logger.info("Synthesizing speech for text: \"%s\"", config.speech.text)

    saved_path = engine.synthesize(
        text=config.speech.text,
        play=config.speech.play,
        save_path=target_path,
    )

    if saved_path:
        logger.info("Synthesized audio successfully saved to: %s", saved_path)

    return ExitCode.SUCCESS


def main(args: list[str] | None = None) -> int:
    """Main application entry point.

    Args:
        args: Optional CLI arguments list.

    Returns:
        int: Process exit code.
    """
    logger = logging.getLogger("main")

    try:
        app_config = parse_args(args)
        setup_logging(verbose=app_config.verbose)

        return run_pipeline(app_config)

    except KeyboardInterrupt:
        logger.warning("\nExecution aborted by user.")
        return ExitCode.INTERRUPTED
    except ValueError as err:
        logger.error("Configuration error: %s", err)
        return ExitCode.INVALID_CONFIG
    except TTSError as err:
        logger.error("TTS Engine error: %s", err)
        return ExitCode.FAILURE
    except Exception as err:
        logger.critical("Unexpected failure: %s", err, exc_info=True)
        return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main())