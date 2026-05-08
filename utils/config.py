"""Centralized configuration — loads environment variables with validation.

Architecture Decision:
    We use a dataclass (not pydantic-settings) to keep dependencies minimal.
    All secrets come from environment variables, never hardcoded.
    The .env file is loaded via python-dotenv for local development.
"""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file if present (local dev only — in Cloud Run, env vars are injected)
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration loaded from environment variables."""

    # ── Gemini (text-to-text translation ONLY — cost-optimized) ──
    gemini_api_key: str
    gemini_text_model: str

    # ── Legal LLM (OpenAI-compatible) ──
    llm_base_url: str
    llm_api_key: str
    llm_model_id: str

    # ── External Speech API (STT/TTS — avoids Gemini audio billing) ──
    speech_api_base_url: str
    speech_api_key: str


def load_config() -> AppConfig:
    """Load and validate configuration from environment variables.

    Raises:
        EnvironmentError: If any required variable is missing.

    """
    required_vars = {
        "GEMINI_API_KEY": "Gemini API key for text translation",
        "GEMINI_TEXT_MODEL": "Gemini model ID for translation",
        "LLM_BASE_URL": "Legal LLM endpoint base URL",
        "LLM_API_KEY": "Legal LLM API key",
        "LLM_MODEL_ID": "Legal LLM model identifier",
        "SPEECH_API_BASE_URL": "Speech API (STT/TTS) base URL",
        "SPEECH_API_KEY": "Speech API key",
    }

    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        details = "\n".join(f"  - {name}: {required_vars[name]}" for name in missing)
        raise OSError(
            f"Missing required environment variables:\n{details}\n\n"
            f"Copy .env.example to .env and fill in the values.",
        )

    return AppConfig(
        gemini_api_key=os.environ["GEMINI_API_KEY"].strip(),
        gemini_text_model=os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash").strip(),
        llm_base_url=os.environ["LLM_BASE_URL"].strip(),
        llm_api_key=os.environ["LLM_API_KEY"].strip(),
        llm_model_id=os.environ["LLM_MODEL_ID"].strip(),
        speech_api_base_url=os.environ["SPEECH_API_BASE_URL"].strip().rstrip("/"),
        speech_api_key=os.environ["SPEECH_API_KEY"].strip(),
    )


# ── Singleton (loaded once per process) ──
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get or create the global config singleton."""
    global _config
    if _config is None:
        _config = load_config()
        logger.info("Configuration loaded successfully.")
    return _config
