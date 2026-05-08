"""Legal LLM service — Ivoirian Labor Law specialist.

Uses an OpenAI-compatible endpoint (not Gemini) for legal inference.
The system prompt grounds the model in Côte d'Ivoire's Code du Travail.

Adapted from: e2e_pipeline.py → get_legal_advice()
"""

import logging

from openai import OpenAI

from utils.config import get_config

logger = logging.getLogger(__name__)

# ── Lazy singleton client ──
_client: OpenAI | None = None

# ── System prompt grounding the model in Ivoirian labor law ──
SYSTEM_PROMPT = """Tu es un expert en droit du travail ivoirien. Tu aides les citoyens de Côte d'Ivoire à comprendre leurs droits.
Règles :
Réponds uniquement en français.
Donne des réponses claires, précises, brèves et directes, sans introduction inutile.
Va directement à l'essentiel : commence par la réponse, puis ajoute une courte explication si nécessaire.
Base tes réponses sur le Code du Travail de Côte d'Ivoire (Loi n° 2015-532 du 20 juillet 2015).
Cite les articles de loi pertinents lorsque c'est possible, sans alourdir la réponse.
Utilise un langage simple et accessible.
N'ajoute aucun avertissement, disclaimer ou conseil externe (ex : “consultez un avocat”).
Si une information est incertaine, indique-le en une phrase courte.
Ne traite que le droit du travail ivoirien.
Reste factuel, neutre et concret.

Style de réponse attendu :

Réponse directe dès la première phrase
Explication courte (2-4 lignes maximum)
Pas de mise en garde, pas de texte inutile"""


def _get_client() -> OpenAI:
    """Get or create the OpenAI client singleton."""
    global _client
    if _client is None:
        config = get_config()
        _client = OpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )
        logger.info("Legal LLM client initialized.")
    return _client


def get_legal_advice(messages: list[dict]) -> str | None:
    """Get legal advice about Ivoirian labor law using conversation history.

    Args:
        messages: List of message dicts (e.g., [{"role": "user", "content": ...}]).
                  The SYSTEM_PROMPT will be automatically prepended.

    Returns:
        Legal response in French, or None if the call fails.

    """
    if not messages:
        logger.warning("Legal LLM: Empty messages provided, skipping.")
        return None

    config = get_config()

    logger.info("Legal LLM: Processing query with %d messages...", len(messages))

    # Prepend system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    try:
        client = _get_client()

        response = client.chat.completions.create(
            model=config.llm_model_id,
            messages=full_messages,
            temperature=0.3,
            # max_tokens=800,
            timeout=100,
        )

        result = response.choices[0].message.content
        if not result or not result.strip():
            logger.warning("Legal LLM: Model returned empty response.")
            return None

        logger.info("Legal LLM: Response received (%d chars).", len(result))
        return result.strip()

    except Exception as e:
        import traceback

        logger.error("Legal LLM: Failed — %s\n%s", e, traceback.format_exc())
        return None
