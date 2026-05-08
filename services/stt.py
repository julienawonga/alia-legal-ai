"""Speech-to-Text service — uses external Bambara STT API.

Cost Optimization:
    We use a dedicated external STT API instead of Gemini to avoid
    Gemini's audio processing billing. Gemini is reserved for text-only
    translation where it excels at lower cost.

Adapted from: e2e_pipeline.py → transcribe()
"""

import logging

import requests

from utils.audio import detect_mime_type
from utils.config import get_config

logger = logging.getLogger(__name__)


def transcribe(audio_bytes: bytes, filename: str = "recording.wav") -> str | None:
    """Transcribe Bambara audio to text using the external STT API.

    Args:
        audio_bytes: Raw audio file bytes.
        filename: Original filename (used for MIME type detection).

    Returns:
        Transcribed Bambara text, or None if transcription fails.

    """
    config = get_config()
    mime_type = detect_mime_type(filename)

    logger.info(
        "STT: Sending %d bytes (%s) to transcribe...", len(audio_bytes), mime_type,
    )

    try:
        headers = {"X-API-Key": config.speech_api_key}
        files = {"audio": (filename, audio_bytes, mime_type)}

        response = requests.post(
            f"{config.speech_api_base_url}/transcribe",
            headers=headers,
            files=files,
            timeout=200,
        )
        response.raise_for_status()

        data = response.json()
        transcription = data.get("transcription", "").strip()

        if not transcription:
            logger.warning("STT: API returned empty transcription.")
            return None

        logger.info("STT: Transcription received (%d chars).", len(transcription))
        return transcription

    except requests.exceptions.Timeout:
        logger.error("STT: Request timed out after 60s.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error("STT: HTTP error %s — %s", e.response.status_code, e.response.text)
        return None
    except Exception as e:
        logger.error("STT: Unexpected error — %s", e)
        return None
