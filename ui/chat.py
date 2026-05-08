"""Chat UI components — message rendering, pipeline visualization, and bilingual content.

All user-facing text is bilingual: French + Bambara translation.
"""


import streamlit as st

from pipeline.orchestrator import StepResult


def init_chat_state():
    """Initialize chat-related session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processing" not in st.session_state:
        st.session_state.processing = False


def add_user_message(text: str, audio_bytes: bytes | None = None):
    """Add a user message to chat history."""
    st.session_state.messages.append(
        {
            "role": "user",
            "content": text,
            "audio": audio_bytes,
        },
    )


def add_assistant_message(result: dict):
    """Add an assistant response to chat history."""
    st.session_state.messages.append(
        {
            "role": "assistant",
            "result": result,
        },
    )


def render_chat_history():
    """Render all messages from chat history."""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            _render_user_message(msg)
        else:
            _render_assistant_message(msg)


def _render_user_message(msg: dict):
    """Render a single user message."""
    with st.chat_message("user"):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/wav")


def _render_assistant_message(msg: dict):
    """Render a single assistant message with pipeline details."""
    result: dict = msg["result"]

    with st.chat_message("assistant", avatar="⚖️"):
        bambara_answer = result.get("bambara_answer")
        if bambara_answer:
            st.markdown(bambara_answer)

        audio_response = result.get("audio_response")
        if audio_response:
            st.audio(audio_response, format="audio/wav")

        french_answer = result.get("french_answer")
        if french_answer:
            with st.expander("Français / Tubabuka", expanded=False):
                st.markdown(french_answer)

        success = result.get("success", False)
        if not success:
            st.error(
                "Désolé, je n'ai pas pu traiter votre question. "
                "Veuillez réessayer ou reformuler.\n\n"
                "*A ka nɔfɛ, n'a se ka aw ni ɲininkali dɔ faara fɔ. "
                "Aw jɔ fla walima aw ka diɲɛ segin.*",
            )


def _render_pipeline_steps(steps: list[StepResult]):
    """Render pipeline step details with status indicators."""
    for step in steps:
        icon = _get_status_icon(step.status)
        time_str = f"{step.duration_ms:.0f}ms" if step.duration_ms > 0 else "—"

        col_icon, col_name, col_time = st.columns([0.5, 5, 1.5])
        with col_icon:
            st.markdown(icon)
        with col_name:
            st.markdown(
                f"<span class='step-name'>{step.name}</span>",
                unsafe_allow_html=True,
            )
        with col_time:
            st.markdown(
                f"<span class='step-time'>{time_str}</span>",
                unsafe_allow_html=True,
            )

        if step.error:
            st.caption(f"❌ {step.error}")


def _get_status_icon(status: str) -> str:
    """Map step status to a display icon."""
    return {"success": "✅", "error": "❌", "skipped": "⏭️"}.get(status, "❓")


def render_welcome_card():
    """Render the welcome card — bilingual (French + Bambara).
    Shown when there are no messages yet.
    """
    st.markdown(
        """
    <div class="welcome-card">
        <h3>🤝 Bienvenue! / I ni ce!</h3>
        <div class="bambara-welcome">
            Aw ni ce, aw ka kɛnɛ wa? — Bienvenue, comment allez-vous?
        </div>
        <p>
            <strong>Alia</strong> est votre assistant legal intelligent pour le
            <strong>droit du travail</strong> en Côte d'Ivoire.<br>
            <em style="color: var(--accent-gold); font-size: 0.82rem;">
                Alia ye aw ka sariya dɛmɛbaga ye, baara sariya la Côte d'Ivoire jamanaden.
            </em>
        </p>
        <p style="font-size: 0.82rem; margin-top: 0.5rem;">
            Parlez ou écrivez en Bambara — Alia vous répond avec une réponse vocale et textuelle.<br>
            <em style="color: var(--accent-gold); font-size: 0.78rem;">
                Aw ye kuma walima aw ye sɛbɛn Bamanankan na — Alia bɛ aw jaabi kan na ani sɛbɛn na.
            </em>
        </p>
        <!--
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">🎤</div>
                <div class="feature-label">Parlez en Bambara</div>
                <div class="feature-bambara">Kuma Bamanankan na</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">⚖️</div>
                <div class="feature-label">Droit du Travail</div>
                <div class="feature-bambara">Baara Sariya</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔊</div>
                <div class="feature-label">Réponse vocale</div>
                <div class="feature-bambara">Jaabi kan na</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🌍</div>
                <div class="feature-label">Inclusion numérique</div>
                <div class="feature-bambara">Bɛɛ ka se ka baara kɛ</div>
            </div>
        </div>
        -->
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_equity_banner():
    """Render the Digital Equity & Inclusivity banner.
    Displayed in the sidebar and on the login page.
    """
    # st.markdown("""
    # <div class="equity-banner">
    #     <div class="equity-title">🌍 Digital Equity & Inclusivity</div>
    #     <div class="equity-text">
    #         Break down barriers through linguistic diversity, intuitive interfaces,
    #         and tools that help close the AI skills gap.
    #     </div>
    #     <div class="equity-bambara">
    #         Danfaraba cɛ fɛɛrɛw bɔ kan caman, fɛɛrɛ nɔgɔman, ani baarakɛminɛnw fɛ
    #         minw bɛ mɔgɔ bɛɛ dɛmɛ ka se ka IA baara kɛ.
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)


def render_impact_sidebar():
    """Render the social impact section in the sidebar — bilingual."""
    st.markdown(
        """
    <div class="impact-banner">
        <p>
            <strong>Impact social / Jama baarakɛcogo</strong><br>
            Alia utilise l'IA pour briser les barrières linguistiques et donner
            accès au droit du travail aux communautés Bambara de Côte d'Ivoire.
        </p>
        <p class="bambara-text">
            Alia bɛ IA baara kɛ ka kan danfarabaw bɔ ani ka Bamanankan kafo mɔgɔw
            dɛmɛ ka baara sariya dɔn.
        </p>
        <!--
        <div style="margin-top: 0.5rem;">
            <span class="impact-stat">🗣️ Bambara</span>
            <span class="impact-stat">⚖️ Baara Sariya</span>
            <span class="impact-stat">🤖 IA inclusive</span>
        </div>
        -->
    </div>
    """,
        unsafe_allow_html=True,
    )
