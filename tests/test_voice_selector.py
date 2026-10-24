"""Unit tests for VoiceSelector models and matching logic."""

from config import VoiceConfig
from voice_selector import DefaultVoiceSelector, VoiceInfo


def test_select_voice_by_name():
    voices = [
        VoiceInfo(id="id-1", name="Microsoft David Desktop - English", languages=["en-US"]),
        VoiceInfo(id="id-2", name="Microsoft Irina Desktop - Russian", languages=["ru-RU"]),
    ]
    selector = DefaultVoiceSelector()
    selected = selector.select_voice(voices, VoiceConfig(language="russian"))

    assert selected is not None
    assert selected.id == "id-2"
    assert "Irina" in selected.name


def test_select_voice_by_language_tag():
    voices = [
        VoiceInfo(id="id-1", name="David", languages=["en-US"]),
        VoiceInfo(id="id-2", name="Elena", languages=["ru-RU"]),
    ]
    selector = DefaultVoiceSelector()
    selected = selector.select_voice(voices, VoiceConfig(language="ru"))

    assert selected is not None
    assert selected.id == "id-2"


def test_select_voice_by_explicit_id():
    voices = [
        VoiceInfo(id="id-1", name="David", languages=["en-US"]),
        VoiceInfo(id="id-2", name="Irina", languages=["ru-RU"]),
    ]
    selector = DefaultVoiceSelector()
    selected = selector.select_voice(voices, VoiceConfig(voice_id="id-1"))

    assert selected is not None
    assert selected.id == "id-1"
    assert selected.name == "David"


def test_select_voice_not_found():
    voices = [
        VoiceInfo(id="id-1", name="David", languages=["en-US"]),
    ]
    selector = DefaultVoiceSelector()
    selected = selector.select_voice(voices, VoiceConfig(language="japanese"))

    assert selected is None


def test_select_voice_empty_list():
    selector = DefaultVoiceSelector()
    selected = selector.select_voice([], VoiceConfig(language="russian"))
    assert selected is None
