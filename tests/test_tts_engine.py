"""Unit tests for TTS engines, interfaces, and pipeline execution."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from config import AppConfig, OutputConfig, SpeechConfig
from main import ExitCode, run_pipeline
from tts_engine import (
    AudioSaveError,
    MockTTSEngine,
    Pyttsx3Engine,
    TTSInitializationError,
)


def test_mock_tts_engine_playback():
    engine = MockTTSEngine()
    engine.configure(rate=180, volume=0.9, voice_id="mock-ru")
    assert engine.current_rate == 180
    assert engine.current_volume == 0.9
    assert engine.current_voice_id == "mock-ru"

    engine.speak("Testing mock speech")
    assert engine.spoken_texts == ["Testing mock speech"]


def test_mock_tts_engine_save_file(tmp_path: Path):
    engine = MockTTSEngine()
    target_file = tmp_path / "mock_audio.wav"

    saved_path = engine.save_to_file("Hello mock", target_file)
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == "MOCK AUDIO: Hello mock"
    assert len(engine.saved_files) == 1


def test_pipeline_with_mock_engine(tmp_path: Path):
    target_dir = tmp_path / "output"
    app_config = AppConfig(
        speech=SpeechConfig(text="Integration test text", play=True),
        output=OutputConfig(save=True, output_dir=target_dir, output_filename="test_file"),
    )
    engine = MockTTSEngine()

    exit_code = run_pipeline(app_config, engine=engine)
    assert exit_code == ExitCode.SUCCESS
    assert "Integration test text" in engine.spoken_texts
    assert len(engine.saved_files) == 1
    assert (target_dir / "test_file.wav").exists()


def test_pipeline_list_voices_with_mock_engine():
    app_config = AppConfig(
        speech=SpeechConfig(play=False),
        output=OutputConfig(save=False),
        list_voices=True,
    )
    engine = MockTTSEngine()

    exit_code = run_pipeline(app_config, engine=engine)
    assert exit_code == ExitCode.SUCCESS
    assert len(engine.spoken_texts) == 0
    assert len(engine.saved_files) == 0


def test_pyttsx3_engine_initialization_error():
    def failing_init():
        raise RuntimeError("Native driver missing")

    engine = Pyttsx3Engine(init_fn=failing_init)
    with pytest.raises(TTSInitializationError, match="Could not initialize pyttsx3 engine"):
        engine.get_voices()


def test_pyttsx3_engine_voices_mapping():
    mock_backend = MagicMock()
    v1 = MagicMock()
    v1.id = "v-1"
    v1.name = "Test Voice"
    v1.languages = [b"en-US"]
    mock_backend.getProperty.return_value = [v1]

    engine = Pyttsx3Engine(init_fn=lambda: mock_backend)
    voices = engine.get_voices()

    assert len(voices) == 1
    assert voices[0].id == "v-1"
    assert voices[0].name == "Test Voice"
    assert voices[0].languages == ["en-US"]


def test_pyttsx3_engine_configure():
    mock_backend = MagicMock()
    engine = Pyttsx3Engine(init_fn=lambda: mock_backend)

    engine.configure(rate=160, volume=0.8, voice_id="v-1")
    mock_backend.setProperty.assert_any_call("rate", 160)
    mock_backend.setProperty.assert_any_call("volume", 0.8)
    mock_backend.setProperty.assert_any_call("voice", "v-1")


def test_pyttsx3_engine_save_error(tmp_path: Path):
    mock_backend = MagicMock()
    mock_backend.save_to_file.side_effect = OSError("Disk write failed")

    engine = Pyttsx3Engine(init_fn=lambda: mock_backend)
    with pytest.raises(AudioSaveError, match="Failed to save audio file"):
        engine.save_to_file("Text", tmp_path / "bad.wav")
