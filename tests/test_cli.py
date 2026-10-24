"""Unit tests for CLI argument parsing."""

from pathlib import Path
from cli import parse_args


def test_parse_args_defaults():
    app_config = parse_args([])
    assert app_config.speech.rate == 150
    assert app_config.speech.volume == 1.0
    assert app_config.speech.play is True
    assert app_config.speech.voice.language == "english"
    assert app_config.speech.voice.voice_id is None
    assert app_config.output.save is True
    assert app_config.output.output_dir == Path("output")
    assert app_config.output.output_filename == "output"
    assert app_config.output.output_extension == "wav"
    assert app_config.list_voices is False
    assert app_config.verbose is False


def test_parse_args_custom_flags():
    args = [
        "-t", "Custom speech sentence",
        "-r", "180",
        "-v", "0.75",
        "-l", "en",
        "--voice-id", "ms-zira",
        "-o", "audio_files",
        "-n", "chapter_1",
        "-e", "wav",
        "--verbose",
    ]
    app_config = parse_args(args)
    assert app_config.speech.text == "Custom speech sentence"
    assert app_config.speech.rate == 180
    assert app_config.speech.volume == 0.75
    assert app_config.speech.voice.language == "en"
    assert app_config.speech.voice.voice_id == "ms-zira"
    assert app_config.output.output_dir == Path("audio_files")
    assert app_config.output.output_filename == "chapter_1"
    assert app_config.output.output_extension == "wav"
    assert app_config.verbose is True


def test_parse_args_no_play_flag():
    args = ["--no-play"]
    app_config = parse_args(args)
    assert app_config.speech.play is False
    assert app_config.output.save is True


def test_parse_args_no_save_flag():
    args = ["--no-save"]
    app_config = parse_args(args)
    assert app_config.speech.play is True
    assert app_config.output.save is False


def test_parse_args_list_voices_flag():
    args = ["--list-voices"]
    app_config = parse_args(args)
    assert app_config.list_voices is True
