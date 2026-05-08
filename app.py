"""⚖️ Alia — Assistant Legal IA pour la Côte d'Ivoire
      Sariya Dɛmɛbaga — Côte d'Ivoire Baara Sariya

Main Streamlit application with authentication and voice-to-voice chat.
Bilingual interface: French + Bambara.

Architecture:
    - streamlit-authenticator for login (YAML credentials, bcrypt hashed)
    - Pipeline runs in-process (no separate backend)
    - Cloud Run deployment via single Dockerfile

Pipeline (cost-optimized):
    Bambara Audio → STT (External API) → Translate BM→FR (Gemini text) →
    Legal LLM (OpenAI) → Translate FR→BM (Gemini text) → TTS (External API) →
    Bambara Audio Response
"""

import logging
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from ui.audio import render_audio_input
from ui.chat import (
    add_assistant_message,
    add_user_message,
    init_chat_state,
    render_chat_history,
    render_equity_banner,
    render_welcome_card,
)
from ui.styles import get_app_css, get_login_css

# removed run_pipeline import

# ── Logging setup ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Page config (MUST be first Streamlit call) ──
st.set_page_config(
    page_title="ALIA - Assistant Legal AI / Sariya Dɛmɛbaga",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="auto",
)

# ── Inject global CSS ──
st.markdown(get_app_css(), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════


def load_auth_config() -> dict:
    """Load authentication config from YAML file."""
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        st.error(
            "Fichier `config.yaml` introuvable. "
            "Créez-le à la racine du projet avec les identifiants.\n\n"
            "*`config.yaml` sɛbɛn ma sɔrɔ. Aw ye a da project kɔnɔ.*",
        )
        st.stop()

    with open(config_path) as f:
        return yaml.load(f, Loader=SafeLoader)


def save_auth_config(config: dict):
    """Persist auth config changes back to YAML."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def render_login_page(authenticator: stauth.Authenticate):
    """Render the login page with bilingual content and equity messaging."""
    st.markdown(get_login_css(), unsafe_allow_html=True)
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)

    # Hero header — bilingual
    st.markdown(
        """
    <div class="hero-container">
        <h1 class="hero-title">Alia</h1>
        <p class="hero-subtitle">
            Assistant Legal AI / <span class="hero-title" style="font-size: inherit;">Sariya Dɛmɛbaga</span>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Login form
    try:
        authenticator.login(
            fields={
                "Form name": "Connexion / Dòn",
                "Username": "Nom d'utilisateur / Tɔgɔ",
                "Password": "Mot de passe / Gundo",
                "Login": "Se connecter / Dòn",
            },
        )
    except Exception as e:
        st.error(f"Erreur d'authentification: {e}")

    # Handle login states
    if st.session_state.get("authentication_status") is False:
        st.error(
            "Nom d'utilisateur ou mot de passe incorrect. / Tɔgɔ walima gundo man ɲi.",
        )
    elif st.session_state.get("authentication_status") is None:
        # Equity & impact messaging below login
        render_equity_banner()

        st.markdown(
            """
        <div class="impact-banner" style="margin-top: 0.75rem;">
            <p>
                <strong>Pourquoi Alia?</strong><br>
                En Côte d'Ivoire, des millions de travailleurs n'ont pas
                accès à l'information légale dans leur langue maternelle.
                Alia utilise l'intelligence artificielle pour combler ce fossé —
                transformant la voix en conseil legal accessible.
            </p>
            <p class="bambara-text">
                <strong>Alia bɛɛ mun? / Mun na Alia?</strong><br>
                I Cote d'Ivoire, kɔrɔn ɲɔgɔnna ka taa kɛra sariya la
                a fɔlɔ ko Bambara kɔrɔn. Alia bɛ miiri la ka taa kɛra
                sariya la — ka taa kan na baara sariya kɛra.
            </p>
            <div style="margin-top: 0.5rem;">
                <span class="impact-stat"><strong>+30M locuteurs Bambara</strong></span>
                <span class="impact-stat">Baara Sariya</span>
                <span class="impact-stat">Kan na</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════
# MAIN CHAT INTERFACE
# ═══════════════════════════════════════════════════════════════


def render_sidebar(authenticator: stauth.Authenticate):
    """Render the sidebar with user info, controls, and impact banner — bilingual."""
    with st.sidebar:
        # User info
        name = st.session_state.get("name", "Utilisateur")
        st.markdown(
            f"""
        <div style="
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(0,0,0,0.08);
            margin-bottom: 0.75rem;
        ">
            <div style="font-size: 0.75rem; color: #9ca3af;">
                Connecté / Dònnen
            </div>
            <div style="
                font-size: 1rem;
                font-weight: 600;
                color: #d97706;
                margin-top: 0.15rem;
            ">
                👤 {name}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Logout
        authenticator.logout("Quitter / Bɔ", key="sidebar_logout")

        st.divider()

        # Input mode selector — bilingual
        st.markdown("### Mode / Baarakɛcogo")
        input_mode = st.radio(
            "Comment poser votre question? / Aw bɛ ɲininkali kɛ cogo di?",
            options=["Voix / Kan", "Texte / Sɛbɛn"],
            index=0,
            key="input_mode",
            label_visibility="collapsed",
        )

        # st.divider()

        # Impact sidebar
        # render_impact_sidebar()

        # About
        st.markdown(
            """
        <div style="
            padding: 0.75rem 0;
            font-size: 0.7rem;
            color: #9ca3af;
            border-top: 1px solid rgba(0,0,0,0.06);
            margin-top: 0.75rem;
        ">
            <strong>Alia v1.0</strong><!--<br>
            Propulsé par Gemini & IA<br>
            Digital Equity & Inclusivity<br>
            <em>Bɛɛ ka se ka baara kɛ</em>-->
        </div>
        """,
            unsafe_allow_html=True,
        )

        return input_mode


def render_main_chat(input_mode: str):
    """Render the main chat interface — bilingual header."""
    # Compact hero
    st.markdown(
        """
    <div class="hero-container" style="padding: 0.75rem 0 0.25rem;">
        <h1 class="hero-title" style="font-size: 1.6rem;">⚖️ Alia</h1>
        <p class="hero-subtitle" style="font-size: 0.82rem;">
            Droit du travail ivoirien — en Bambara / Baara Sariya — Bamanankan na
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Initialize chat state
    init_chat_state()

    # Welcome card if no messages
    if not st.session_state.messages:
        render_welcome_card()

    # Chat history
    render_chat_history()

    # Input area
    if "Voix" in input_mode:
        _handle_audio_input()
    else:
        _handle_text_input()


def _handle_audio_input():
    """Handle voice/audio input mode."""
    audio_bytes, filename = render_audio_input()

    if audio_bytes:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.audio(audio_bytes, format="audio/wav")
        with col2:
            send_pressed = st.button(
                "Envoyer / Ci",
                key="send_audio",
                use_container_width=True,
            )

        if send_pressed:
            _process_input(audio_bytes=audio_bytes, filename=filename)


def _handle_text_input():
    """Handle text input mode."""
    user_text = st.chat_input(
        "Aw ka ɲininkali sɛbɛn Bamanankan na... / Écrivez en Bambara...",
        key="text_input",
    )

    if user_text:
        _process_input(text_input=user_text)


def _process_input(
    audio_bytes: bytes = None,
    text_input: str = None,
    filename: str = "recording.wav",
):
    """Process user input through the LangGraph pipeline."""
    display_text = (
        text_input or "🎤 [Kan kuma / Message vocal en Bambara]"
    )

    # Add user message to history
    add_user_message(display_text, audio_bytes)

    # Show user message
    with st.chat_message("user"):
        st.markdown(display_text)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")

    # Ensure we have a thread_id for LangGraph memory
    if "thread_id" not in st.session_state:
        import uuid

        st.session_state.thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # Run pipeline
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Alia bɛ miiri la... / Traitement en cours"):
            try:
                from pipeline.orchestrator import get_pipeline

                pipeline = get_pipeline()

                # Initial state for this turn
                initial_state = {
                    "input_mode": "audio" if audio_bytes else "text",
                    "audio_bytes": audio_bytes,
                    "text_input": text_input,
                    "filename": filename,
                    "steps": [],
                }

                # Invoke the graph
                final_state = pipeline.invoke(initial_state, config=config)

                # Display response
                bambara_answer = final_state.get("bambara_answer")
                audio_response = final_state.get("audio_response")
                french_answer = final_state.get("french_answer")
                steps = final_state.get("steps", [])
                success = final_state.get("success", False)

                if bambara_answer:
                    st.markdown(bambara_answer)

                if audio_response:
                    st.audio(audio_response, format="audio/wav")

                if french_answer:
                    with st.expander(
                        "Réponse en Français / Jaabi Tubabukan na", expanded=False,
                    ):
                        st.markdown(french_answer)

                if not success:
                    st.error(
                        "Le pipeline n'a pas pu compléter. / Baarakɛcogo ma se ka dafa.",
                    )

                # Save to UI history
                add_assistant_message(final_state)

            except Exception as e:
                logger.error("Pipeline execution failed: %s", e)
                st.error(f"Erreur inattendue / Fili: {e}")


# ═══════════════════════════════════════════════════════════════
# APP ENTRY POINT
# ═══════════════════════════════════════════════════════════════


def main():
    """Application entry point."""
    config = load_auth_config()

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    if st.session_state.get("authentication_status"):
        # ── Authenticated: show chat ──
        input_mode = render_sidebar(authenticator)
        render_main_chat(input_mode)
        save_auth_config(config)
    else:
        # ── Not authenticated: show login ──
        render_login_page(authenticator)
        save_auth_config(config)


if __name__ == "__main__":
    main()
