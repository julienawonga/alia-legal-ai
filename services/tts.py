"""Text-to-Speech service — uses external Bambara TTS API.

Cost Optimization:
    We use a dedicated external TTS API instead of Gemini to avoid
    Gemini's audio generation billing. The external API is specialized
    for Bambara speech synthesis.

Adapted from: e2e_pipeline.py → synthesize()
"""

import logging

import requests

from utils.config import get_config

logger = logging.getLogger(__name__)


def synthesize(text: str) -> bytes | None:
    """Synthesize Bambara text into speech audio using the external TTS API.

    Args:
        text: Bambara text to convert to speech.

    Returns:
        WAV audio bytes, or None if synthesis fails.

    """
    if not text or not text.strip():
        logger.warning("TTS: Empty text provided, skipping synthesis.")
        return None

    config = get_config()

    logger.info("TTS: Synthesizing %d chars of Bambara text...", len(text))

    try:
        headers = {"X-API-Key": config.speech_api_key}
        payload = {"text": text.strip()}

        response = requests.post(
            f"{config.speech_api_base_url}/synthesize",
            json=payload,
            headers=headers,
            timeout=200,
        )
        response.raise_for_status()

        audio_bytes = response.content

        if not audio_bytes or len(audio_bytes) < 100:
            logger.warning(
                "TTS: API returned suspiciously small audio (%d bytes).",
                len(audio_bytes),
            )
            return None

        logger.info("TTS: Audio generated successfully (%d bytes).", len(audio_bytes))
        return audio_bytes

    except requests.exceptions.Timeout:
        logger.error("TTS: Request timed out after 60s.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error("TTS: HTTP error %s — %s", e.response.status_code, e.response.text)
        return None
    except Exception as e:
        logger.error("TTS: Unexpected error — %s", e)
        return None
