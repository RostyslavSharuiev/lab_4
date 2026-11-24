"""Text translation interfaces and implementations."""

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Raised when text translation fails."""


class ITranslator(Protocol):
    """Interface for text translation strategies."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source_lang to target_lang."""
        ...


class GoogleTranslatorAdapter:
    """Translator that tries several online services until one succeeds."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        from deep_translator import GoogleTranslator, MyMemoryTranslator

        # Кожен елемент: (назва, функція, що створює перекладач)
        providers = [
            ("Google", lambda: GoogleTranslator(source=source_lang, target=target_lang)),
            ("MyMemory", lambda: MyMemoryTranslator(source="uk-UA", target="en-GB")),
        ]

        last_error: Exception | None = None

        for name, factory in providers:
            try:
                logger.info("Trying translation provider: %s", name)
                result = factory().translate(text)
                if result and result.strip():
                    logger.info("Translation succeeded via %s", name)
                    return result
                logger.warning("%s returned an empty result.", name)
            except Exception as err:
                logger.warning("Provider %s failed: %s", name, err)
                last_error = err

        raise TranslationError(f"All translation providers failed. Last error: {last_error}")


class MockTranslator:
    """Fake translator for tests (no internet needed)."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"[{source_lang}->{target_lang}] {text}"