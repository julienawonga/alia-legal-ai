"""LangGraph Pipeline orchestrator — runs the voice-to-voice legal assistant flow
with local memory compression to handle the 24000-token limit.

Pipeline Nodes:
    1. STT:             Bambara audio → Bambara text
    2. TranslateIn:     Bambara text → French text
    3. CompressMemory:  Summarizes old French messages if context > ~700 tokens
    4. LegalLLM:        French context + French question → French answer
    5. TranslateOut:    French answer → Bambara text
    6. TTS:             Bambara text → Bambara audio
"""

import logging
import operator
import time
from dataclasses import dataclass
from typing import Annotated, TypedDict

import tiktoken
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from services.legal_llm import get_legal_advice
from services.stt import transcribe
from services.translation import (
    summarize_history,
    translate_bm_to_fr,
    translate_fr_to_bm,
)
from services.tts import synthesize

logger = logging.getLogger(__name__)


# ── Metadata Types ──


@dataclass
class StepResult:
    """Result of a single pipeline step."""

    name: str
    status: str  # "success", "error", "skipped"
    duration_ms: float = 0.0
    output: str | None = None
    error: str | None = None


# ── State Definition ──


class AgentState(TypedDict):
    """The state of the LangGraph agent."""

    # Memory
    messages: Annotated[list[AnyMessage], operator.add]
    summary: str

    # Current turn inputs
    input_mode: str
    audio_bytes: bytes | None
    filename: str
    text_input: str | None

    # Current turn intermediate results
    bambara_input: str | None
    french_question: str | None
    french_answer: str | None
    bambara_answer: str | None
    audio_response: bytes | None

    # Tracking
    steps: list[StepResult]
    turn_start_time: float
    success: bool


# ── Helper functions ──


def _count_tokens(text: str) -> int:
    """Estimate token count for the LLM context."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def _run_step(
    name: str, state: AgentState, fn, *args, **kwargs,
) -> tuple[any, StepResult]:
    """Execute a function with timing and logging, returning (result, StepResult)."""
    start = time.monotonic()
    try:
        result = fn(*args, **kwargs)
        elapsed = (time.monotonic() - start) * 1000

        if result is None:
            return None, StepResult(
                name=name,
                status="error",
                duration_ms=elapsed,
                error="Service returned no result.",
            )

        output_preview = (
            str(result)[:150]
            if not isinstance(result, bytes)
            else f"{len(result)} bytes"
        )
        return result, StepResult(
            name=name, status="success", duration_ms=elapsed, output=output_preview,
        )

    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        logger.error("Pipeline step '%s' failed: %s", name, e)
        return None, StepResult(
            name=name, status="error", duration_ms=elapsed, error=str(e),
        )


# ── Nodes ──


def node_stt(state: AgentState) -> dict:
    steps = []
    bambara_input = None

    if state.get("audio_bytes"):
        bambara_input, step = _run_step(
            "Transcription (STT)",
            state,
            transcribe,
            state["audio_bytes"],
            state.get("filename", "audio.wav"),
        )
        steps.append(step)
    else:
        bambara_input = state.get("text_input")
        steps.append(
            StepResult(
                name="Saisie texte", status="skipped", output="Direct text input.",
            ),
        )

    return {"bambara_input": bambara_input, "steps": steps}


def node_translate_in(state: AgentState) -> dict:
    if not state.get("bambara_input"):
        return {
            "steps": [
                StepResult("Traduction BM→FR", "error", error="Missing Bambara input."),
            ],
        }

    french_question, step = _run_step(
        "Traduction BM→FR", state, translate_bm_to_fr, state["bambara_input"],
    )

    if not french_question:
        french_question = state["bambara_input"]  # Fallback
        step.error = "Fallback to raw input"

    return {"french_question": french_question, "steps": [step]}


def node_compress_memory(state: AgentState) -> dict:
    """Compresses older messages if token count is high (limit 32768)."""
    messages = state.get("messages", [])
    summary = state.get("summary", "")

    # Calculate current token load (approximate)
    history_text = (
        summary
        + "\n"
        + "\n".join(
            [m.content for m in messages if isinstance(m, (HumanMessage, AIMessage))],
        )
    )
    token_count = _count_tokens(history_text)

    # If safe, do nothing
    if token_count < 24000:
        return {
            "steps": [
                StepResult(
                    "Compression Mémoire",
                    "skipped",
                    output=f"Tokens: {token_count}/24000 - Safe",
                ),
            ],
        }

    # Too large -> Summarize history
    new_summary, step = _run_step(
        "Compression Mémoire (Gemini)", state, summarize_history, history_text,
    )

    if new_summary:
        return {"summary": new_summary, "steps": [step]}
    return {"steps": [step]}


def node_llm(state: AgentState) -> dict:
    if not state.get("french_question"):
        return {
            "steps": [
                StepResult(
                    "⚖️ Consultation (LLM)", "error", error="Missing French question.",
                ),
            ],
        }

    # Build context for Legal LLM
    llm_messages = []

    # Add summary if it exists
    if state.get("summary"):
        llm_messages.append(
            {
                "role": "system",
                "content": f"Résumé des échanges précédents:\n{state['summary']}",
            },
        )

    # Add recent uncompressed history (last 4 messages to be safe)
    recent_msgs = state.get("messages", [])[-4:]
    for m in recent_msgs:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        llm_messages.append({"role": role, "content": m.content})

    # Add current question
    llm_messages.append({"role": "user", "content": state["french_question"]})

    # Call LLM
    french_answer, step = _run_step(
        "⚖️ Consultation (LLM)", state, get_legal_advice, llm_messages,
    )

    if not french_answer:
        return {"steps": [step], "success": False}

    # Add new messages to graph state
    new_messages = [
        HumanMessage(content=state["french_question"]),
        AIMessage(content=french_answer),
    ]

    return {
        "french_answer": french_answer,
        "messages": new_messages,
        "steps": [step],
        "success": True,
    }


def node_translate_out(state: AgentState) -> dict:
    if not state.get("french_answer"):
        return {"steps": []}

    bambara_answer, step = _run_step(
        "🔄 Traduction FR→BM", state, translate_fr_to_bm, state["french_answer"],
    )

    if not bambara_answer:
        bambara_answer = state["french_answer"]  # Fallback
        step.error = "Fallback to French"

    return {"bambara_answer": bambara_answer, "steps": [step]}


def node_tts(state: AgentState) -> dict:
    if not state.get("bambara_answer"):
        return {"steps": []}

    audio, step = _run_step(
        "Synthèse vocale (TTS)", state, synthesize, state["bambara_answer"],
    )

    return {"audio_response": audio, "steps": [step]}


# ── Graph Definition ──


def build_graph() -> StateGraph:
    """Build and compile the LangGraph workflow."""
    builder = StateGraph(AgentState)

    builder.add_node("stt", node_stt)
    builder.add_node("translate_in", node_translate_in)
    builder.add_node("compress", node_compress_memory)
    builder.add_node("llm", node_llm)
    builder.add_node("translate_out", node_translate_out)
    builder.add_node("tts", node_tts)

    builder.add_edge(START, "stt")
    builder.add_edge("stt", "translate_in")
    builder.add_edge("translate_in", "compress")
    builder.add_edge("compress", "llm")
    builder.add_edge("llm", "translate_out")
    builder.add_edge("translate_out", "tts")
    builder.add_edge("tts", END)

    return builder


# Global cached graph
_graph = None
_checkpointer = MemorySaver()


def get_pipeline():
    """Get the compiled LangGraph pipeline with native memory checkpointer."""
    global _graph
    if _graph is None:
        _graph = build_graph().compile(checkpointer=_checkpointer)
    return _graph
