"""Unit tests for configuration models: VoiceConfig, SpeechConfig, OutputConfig, and AppConfig."""

from pathlib import Path
import pytest

from config import AppConfig, OutputConfig, SpeechConfig, VoiceConfig


def test_default_voice_config():
    config = VoiceConfig()
    assert config.language == "english"
    assert config.voice_id is None


def test_invalid_voice_config():
    with pytest.raises(ValueError, match="Either a non-empty voice language or a voice ID"):
        VoiceConfig(language="  ", voice_id=None)


def test_default_speech_config():
    config = SpeechConfig()
    assert config.rate == 150
    assert config.volume == 1.0
    assert config.play is True
    assert "local speech synthesis" in config.text.lower()
    assert config.voice.language == "english"


def test_custom_speech_config():
    voice = VoiceConfig(language="en", voice_id="custom-voice-123")
    config = SpeechConfig(
        text="Hello, World!",
        rate=200,
        volume=0.8,
        play=False,
        voice=voice,
    )
    assert config.text == "Hello, World!"
    assert config.rate == 200
    assert config.volume == 0.8
    assert config.play is False
    assert config.voice.voice_id == "custom-voice-123"


def test_invalid_speech_rate():
    with pytest.raises(ValueError, match="Speech rate must be positive"):
        SpeechConfig(rate=0)

    with pytest.raises(ValueError, match="Speech rate must be positive"):
        SpeechConfig(rate=-50)


def test_invalid_speech_volume():
    with pytest.raises(ValueError, match="Speech volume must be between 0.0 and 1.0"):
        SpeechConfig(volume=-0.1)

    with pytest.raises(ValueError, match="Speech volume must be between 0.0 and 1.0"):
        SpeechConfig(volume=1.5)


def test_empty_speech_text():
    with pytest.raises(ValueError, match="Speech text cannot be empty"):
        SpeechConfig(text="   ")


def test_default_output_config():
    config = OutputConfig()
    assert config.save is True
    assert config.output_dir == Path("output")
    assert config.output_filename == "output"
    assert config.output_extension == "wav"
    assert config.file_path == Path("output/output.wav")


def test_custom_output_config():
    config = OutputConfig(
        save=False,
        output_dir=Path("custom_audio"),
        output_filename="lecture_1",
        output_extension=".mp3",
    )
    assert config.save is False
    assert config.output_dir == Path("custom_audio")
    assert config.output_filename == "lecture_1"
    assert config.output_extension == "mp3"
    assert config.file_path == Path("custom_audio/lecture_1.mp3")


def test_output_file_path_with_suffix():
    config = OutputConfig(output_dir=Path("records"), output_filename="demo", output_extension="wav")
    assert config.file_path_with_suffix("_processed") == Path("records/demo_processed.wav")


def test_invalid_output_filename():
    with pytest.raises(ValueError, match="Output filename cannot be empty"):
        OutputConfig(output_filename="  ")


def test_invalid_output_extension():
    with pytest.raises(ValueError, match="Output extension cannot be empty"):
        OutputConfig(output_extension="...")


def test_app_config_validation_requires_action():
    speech = SpeechConfig(play=False)
    output = OutputConfig(save=False)
    with pytest.raises(ValueError, match="At least one action .* must be enabled"):
        AppConfig(speech=speech, output=output, list_voices=False)


def test_app_config_list_voices_allowed_without_actions():
    speech = SpeechConfig(play=False)
    output = OutputConfig(save=False)
    # Should not raise when list_voices is True
    app_config = AppConfig(speech=speech, output=output, list_voices=True)
    assert app_config.list_voices is True
