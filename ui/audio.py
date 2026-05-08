"""Audio input/output UI components.

Provides:
    - Microphone recording via st.audio_input()
    - File upload for pre-recorded audio
    - Audio playback for TTS responses
"""


import streamlit as st


def render_audio_input() -> tuple[bytes | None, str]:
    """Render audio input UI with tabs for microphone and file upload.

    Returns:
        Tuple of (audio_bytes, filename). Both None if no audio provided.

    """
    tab_mic, tab_file = st.tabs(["🎙️ Microphone", "📁 Fichier audio"])

    audio_bytes = None
    filename = "recording.wav"

    with tab_mic:
        audio_value = st.audio_input(
            "Enregistrez votre question en Bambara",
            key="mic_input",
        )
        if audio_value:
            audio_bytes = audio_value.getvalue()
            filename = "recording.wav"

    with tab_file:
        uploaded = st.file_uploader(
            "Téléchargez un fichier audio",
            type=["wav", "mp3", "m4a", "ogg", "flac", "webm"],
            key="file_input",
            help="Formats supportés: WAV, MP3, M4A, OGG, FLAC, WebM",
        )
        if uploaded:
            audio_bytes = uploaded.getvalue()
            filename = uploaded.name

    return audio_bytes, filename


def render_audio_player(audio_bytes: bytes, label: str = "🔊 Réponse audio"):
    """Render an audio player for the TTS response.

    Args:
        audio_bytes: WAV audio bytes to play.
        label: Label displayed above the player.

    """
    if audio_bytes:
        st.markdown(f"**{label}**")
        st.audio(audio_bytes, format="audio/wav")
