# 🗣️ Text-to-Speech (TTS) Synthesizer CLI

A production-grade, cross-platform Python command-line utility for local speech synthesis, audio playback, and audio file generation (`WAV`) using `pyttsx3`.

Built with Python 3.12+, refactored in strict accordance with **SOLID** software design principles, and managed with `uv`.

---

## 🌟 Features

- 🔊 **Local Text-to-Speech**: Offline speech synthesis via `pyttsx3` without external cloud API dependencies.
- 📁 **Audio File Export**: Automatically persists speech to WAV format in an organized destination directory (`output/`).
- 👥 **Intelligent Voice Selection**: Automatically discovers system voices and matches requested languages (e.g. Russian, English) or explicit voice IDs.
- 📋 **Voice Discovery**: Built-in `--list-voices` command to inspect all installed system speech tokens and locale tags.
- ⚙️ **Configurable Parameters**: Custom speech text, speech rate (words per minute), volume level, and output directories.
- 🔇 **Flexible Playback Control**: Toggles for silent audio file generation (`--no-play`) or playback-only mode (`--no-save`).
- 🪵 **Structured Logging**: Timestamps, log levels, and contextual logging.
- 🚦 **Standardized Exit Codes**: Predictable process exit codes (`ExitCode`) for automation and scripting.
- 🧪 **Unit Tested**: Comprehensive test suite covering CLI parsing, domain models, voice selection strategies, and engine execution via `pytest`.

---

## 📋 Prerequisites

- **Python**: `>= 3.12`
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`

---

## 🚀 Quick Start

### 1. Install Dependencies

Using `uv`:
```bash
uv sync
```

---

## 📖 Usage

### Basic Speech Synthesis (Default: English voice, rate 150, volume 1.0)

```bash
uv run python main.py
```
*Synthesizes the default phrase, plays it through the speakers, and saves `output/output.wav`.*

### Custom Phrase and Parameters

Synthesize custom text at a speed of 180 wpm, volume 0.8, and save to `output/lecture_1.wav`:

```bash
uv run python main.py -t "Hello world!" -r 180 -v 0.8 -n lecture_1
```

### Inspect Available Voices

```bash
uv run python main.py --list-voices
```

### Headless / Export-Only (No Sound through Speakers)

Generate the audio file silently:

```bash
uv run python main.py -t "Background generation of an audio file" -n silent_speech --no-play
```

---

## ⚙️ CLI Arguments Reference

### Speech Settings
| Flag | Long Flag    | Default      | Description                                                         |
|------|--------------|--------------|---------------------------------------------------------------------|
| `-t` | `--text`     | Default text | Text to synthesize into speech                                      |
| `-r` | `--rate`     | `150`        | Speech speed rate in words per minute                               |
| `-v` | `--volume`   | `1.0`        | Speech volume level between `0.0` and `1.0`                         |
| `-l` | `--lang`     | `english`    | Language query keyword or locale code (e.g., `english`, `en`, `ru`) |
|      | `--voice-id` | `None`       | Explicit system voice token/identifier                              |

### Output File Settings
| Flag  | Long Flag      | Default  | Description                                        |
|-------|----------------|----------|----------------------------------------------------|
| `-o`  | `--output-dir` | `output` | Target directory path for audio files              |
| `-n`  | `--name`       | `output` | Output filename (without extension)                |
| `-e`  | `--ext`        | `wav`    | Audio container file extension                     |
|       | `--no-save`    | `False`  | Disable saving synthesized audio to disk           |

### Playback & Utility Settings
| Flag   | Long Flag       | Default | Description                                        |
|--------|-----------------|---------|----------------------------------------------------|
|        | `--no-play`     | `False` | Disable real-time speaker audio playback           |
|        | `--list-voices` | `False` | List all available system voices and exit          |
|        | `--verbose`     | `False` | Enable verbose debug log messages                  |

---

## 🧪 Running Tests

To run the unit test suite using `pytest`:

```bash
uv run pytest
```

---

## 📁 Project Structure

```text
lab-4/
├── cli.py            # CLI argument parser & configuration mapping
├── config.py         # Domain models: VoiceConfig, SpeechConfig, OutputConfig, AppConfig
├── logger.py         # Application logging configuration
├── main.py           # Application pipeline orchestration & exit codes
├── pyproject.toml    # Project metadata, dependencies, & tool configs
├── tts_engine.py     # TTS interfaces (ITTSEngine, ISP protocols), Pyttsx3Engine, MockTTSEngine
├── voice_selector.py # Voice selection strategy & VoiceInfo model
├── tests/            # Unit test suite
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_tts_engine.py
│   └── test_voice_selector.py
└── output/           # Default directory for generated WAV audio files
```

---

## 🚦 Exit Codes

| Code  | Name             | Description                                          |
|-------|------------------|------------------------------------------------------|
| `0`   | `SUCCESS`        | Successful execution                                 |
| `1`   | `FAILURE`        | TTS engine error, speech hardware error, or IO fault |
| `2`   | `INVALID_CONFIG` | Invalid configuration or CLI arguments               |
| `130` | `INTERRUPTED`    | Process interrupted by user (`Ctrl+C`)               |
