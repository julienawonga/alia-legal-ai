"""Translation service — Bambara ↔ French using Gemini (text-to-text only).

Cost Optimization:
    Gemini is used ONLY for text-to-text translation, which is significantly
    cheaper than audio processing. All audio operations use the dedicated
    external STT/TTS API instead.

Adapted from: e2e_pipeline.py → translate()
"""

import logging

from google import genai
from google.genai import types

from utils.config import get_config

logger = logging.getLogger(__name__)

# ── Language metadata ──
LANGUAGE_NAMES = {
    "bm": "Bambara (Bamanankan)",
    "fr": "French (Français)",
}

# ── Lazy singleton client ──
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Get or create the Gemini client singleton."""
    global _client
    if _client is None:
        config = get_config()
        _client = genai.Client(api_key=config.gemini_api_key)
        logger.info("Gemini client initialized for translation.")
    return _client


def translate(
    text: str,
    source_lang: str = "bm",
    target_lang: str = "fr",
) -> str | None:
    """Translate text between Bambara and French using Gemini.

    Args:
        text: The text to translate.
        source_lang: ISO 639-1 code ("bm" for Bambara, "fr" for French).
        target_lang: ISO 639-1 code.

    Returns:
        Translated text, or None if translation fails.

    """
    if not text or not text.strip():
        logger.warning("Translation: Empty text provided, skipping.")
        return None

    source_name = LANGUAGE_NAMES.get(source_lang, source_lang)
    target_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    config = get_config()

    prompt = (
        f"Translate the following text from {source_name} to {target_name}.\n"
        f"Output ONLY the translation, nothing else. No explanations, no notes.\n\n"
        f"Text to translate:\n{text}"
    )

    logger.info(
        "Translation: %s → %s (%d chars)...",
        source_lang.upper(),
        target_lang.upper(),
        len(text),
    )

    try:
        client = _get_client()

        response = client.models.generate_content(
            model=config.gemini_text_model,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ],
        )

        result = response.text.strip() if response.text else ""

        if not result:
            logger.warning("Translation: Gemini returned empty response.")
            return None

        logger.info(
            "Translation: Success (%d chars → %d chars).", len(text), len(result),
        )
        return result

    except Exception as e:
        logger.error("Translation: Failed — %s", e)
        return None


def translate_bm_to_fr(text: str) -> str | None:
    """Convenience: Translate Bambara → French."""
    return translate(text, source_lang="bm", target_lang="fr")


def translate_fr_to_bm(text: str) -> str | None:
    """Convenience: Translate French → Bambara."""
    return translate(text, source_lang="fr", target_lang="bm")


def summarize_history(history_text: str) -> str | None:
    """Compress a conversation history into a dense summary using Gemini.

    Args:
        history_text: Formatted string of the previous conversation.

    Returns:
        A dense summary string, or None if it fails.

    """
    if not history_text or not history_text.strip():
        return None

    config = get_config()

    prompt = (
        "Résume la conversation légale suivante de manière concise.\n"
        "Garde tous les détails importants, les faits, et les conseils donnés.\n"
        "Ce résumé servira de contexte pour les prochaines questions.\n\n"
        f"Conversation:\n{history_text}"
    )

    logger.info("Translation: Summarizing history (%d chars)...", len(history_text))

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=config.gemini_text_model,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ],
        )

        result = response.text.strip() if response.text else ""
        if result:
            logger.info("Translation: Summary generated (%d chars).", len(result))
            return result
        return None

    except Exception as e:
        logger.error("Translation: Summarization failed — %s", e)
        return None
