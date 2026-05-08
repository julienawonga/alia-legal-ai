"""Audio utility functions — format detection and helpers.

Adapted from the reference e2e_pipeline.py.
"""

import mimetypes

# Supported audio MIME types for STT upload
SUPPORTED_AUDIO_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
    "audio/ogg",
    "audio/flac",
    "audio/aiff",
    "audio/webm",
}


def detect_mime_type(filename: str) -> str:
    """Detect MIME type from filename extension.

    Falls back to 'audio/wav' if detection fails, since Streamlit's
    st.audio_input() always records WAV.
    """
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type and mime_type in SUPPORTED_AUDIO_TYPES:
        return mime_type
    return "audio/wav"


def validate_audio_bytes(audio_bytes: bytes) -> bool:
    """Basic validation that we have non-empty audio data."""
    return audio_bytes is not None and len(audio_bytes) > 0


def get_audio_extension(mime_type: str) -> str:
    """Get file extension from MIME type."""
    extensions = {
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/mp4": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/ogg": ".ogg",
        "audio/flac": ".flac",
        "audio/aiff": ".aiff",
        "audio/webm": ".webm",
    }
    return extensions.get(mime_type, ".wav")
