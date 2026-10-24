"""Voice selection models and strategies for matching system voices."""

import logging
from dataclasses import dataclass, field
from typing import Protocol

from config import VoiceConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VoiceInfo:
    """Representation of an available speech synthesizer voice.

    Attributes:
        id: Unique system identifier / token for the voice.
        name: Human-readable display name of the voice.
        languages: List of language codes or identifiers supported by this voice.
    """

    id: str
    name: str
    languages: list[str] = field(default_factory=list)


class IVoiceSelector(Protocol):
    """Interface for voice selection strategies."""

    def select_voice(self, voices: list[VoiceInfo], config: VoiceConfig) -> VoiceInfo | None:
        """Select a matching voice from available voices based on configuration criteria.

        Args:
            voices: Available voices discovered from the system.
            config: Voice criteria including requested language or explicit voice ID.

        Returns:
            Matching VoiceInfo if found, or None.
        """
        ...


class DefaultVoiceSelector:
    """Default strategy for voice discovery and matching.

    Supports matching by specific voice ID or searching name and language tags.
    """

    def select_voice(self, voices: list[VoiceInfo], config: VoiceConfig) -> VoiceInfo | None:
        """Find a voice matching the requested ID or language keyword.

        Args:
            voices: Available voices discovered from the system.
            config: Voice configuration specifying search criteria.

        Returns:
            The selected VoiceInfo if matched, or None.
        """
        if not voices:
            logger.warning("No system voices provided for selection.")
            return None

        # 1. Exact or partial match on voice ID if specified
        if config.voice_id:
            target_id = config.voice_id.strip()
            for voice in voices:
                if target_id == voice.id or target_id.lower() in voice.id.lower():
                    logger.info("Found voice matching explicit ID: '%s'", voice.name)
                    return voice
            logger.warning("No voice found matching explicit voice ID: '%s'", config.voice_id)
            return None

        # 2. Search by language keyword in voice name or language tags
        query = config.language.strip().lower()
        for voice in voices:
            name_lower = voice.name.lower()
            langs_lower = [str(lang).lower() for lang in voice.languages]

            # Check if query matches voice name (e.g., 'russian' in 'Microsoft Irina Desktop - Russian')
            if query in name_lower:
                logger.info("Matched voice '%s' by name query '%s'", voice.name, query)
                return voice

            # Check if query matches language tags (e.g., 'ru' in ['ru-ru'])
            if any(query in lang for lang in langs_lower):
                logger.info("Matched voice '%s' by language tag '%s'", voice.name, query)
                return voice

        logger.warning(
            "No voice found matching language query '%s'. Available voices: %s",
            query,
            [v.name for v in voices],
        )
        return None
