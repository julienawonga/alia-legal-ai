"""Premium UI styles — clean light theme with warm amber/gold accents.

Design philosophy:
    - Clean, modern light theme (white/cream base)
    - Warm amber/gold accents reflecting West African aesthetics
    - Compact form elements (no oversized inputs)
    - Smooth micro-animations for engagement
    - Accessible contrast ratios
    - Bilingual-ready (French + Bambara)
"""


def get_app_css() -> str:
    """Return the complete CSS for the application."""
    return """
    <style>
    /* ══════════════════════════════════════════════════════════
       DESIGN TOKENS — LIGHT THEME
       ══════════════════════════════════════════════════════════ */
    :root {
        --bg-primary: #fafafa;
        --bg-secondary: #ffffff;
        --bg-card: rgba(255, 255, 255, 0.85);
        --bg-glass: rgba(255, 255, 255, 0.6);
        --bg-glass-hover: rgba(255, 255, 255, 0.9);
        --bg-warm: #fffbf0;

        --accent-gold: #d97706;
        --accent-gold-light: #f59e0b;
        --accent-amber: #b45309;
        --accent-green: #059669;
        --accent-red: #dc2626;
        --accent-blue: #2563eb;
        --accent-teal: #0d9488;

        --text-primary: #1f2937;
        --text-secondary: #4b5563;
        --text-muted: #9ca3af;
        --text-accent: #92400e;

        --border-subtle: rgba(0, 0, 0, 0.08);
        --border-accent: rgba(217, 119, 6, 0.3);
        --border-medium: rgba(0, 0, 0, 0.12);

        --gradient-hero: linear-gradient(135deg, #d97706 0%, #b45309 50%, #92400e 100%);
        --gradient-warm: linear-gradient(135deg, #fffbf0 0%, #fef3c7 100%);
        --gradient-card: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(255,251,240,0.7));

        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.1);
        --shadow-glow: 0 0 30px rgba(217, 119, 6, 0.08);
        --shadow-button: 0 2px 8px rgba(217, 119, 6, 0.2);

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;

        --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ══════════════════════════════════════════════════════════
       GLOBAL BASE
       ══════════════════════════════════════════════════════════ */
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    .stApp > header {
        background: transparent !important;
    }

    #MainMenu, footer, .stDeployButton {
        display: none !important;
    }

    /* Reduce Streamlit's default large padding to prevent scrolling */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* ══════════════════════════════════════════════════════════
       SIDEBAR
       ══════════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p {
        color: var(--text-secondary) !important;
    }

    /* ══════════════════════════════════════════════════════════
       HERO HEADER
       ══════════════════════════════════════════════════════════ */
    .hero-container {
        text-align: center;
        padding: 1rem 1rem 0.5rem;
        margin-bottom: 0.25rem;
    }

    /* Hero icon removed */

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: var(--gradient-hero);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.1;
    }

    .hero-subtitle {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin-top: 0.4rem;
        font-weight: 400;
    }

    .hero-bambara {
        font-size: 0.8rem;
        color: var(--accent-amber);
        font-style: italic;
        margin-top: 0.15rem;
    }

    .hero-tagline {
        font-size: 0.75rem;
        color: var(--text-accent);
        margin-top: 0.6rem;
        padding: 0.35rem 1rem;
        display: inline-block;
        border: 1px solid var(--border-accent);
        border-radius: 999px;
        background: rgba(217, 119, 6, 0.05);
    }

    /* ══════════════════════════════════════════════════════════
       IMPACT BANNER
       ══════════════════════════════════════════════════════════ */
    .impact-banner {
        background: var(--gradient-warm);
        border: 1px solid var(--border-accent);
        border-radius: var(--radius-lg);
        padding: 0.8rem 1.3rem;
        margin: 0.25rem 0 0.5rem;
        box-shadow: var(--shadow-sm);
    }

    .impact-banner p {
        color: var(--text-secondary) !important;
        font-size: 0.82rem;
        margin: 0;
        line-height: 1.6;
    }

    .impact-banner .bambara-text {
        color: var(--accent-amber) !important;
        font-style: italic;
        font-size: 0.78rem;
        margin-top: 0.4rem;
    }

    .impact-stat {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        background: rgba(217, 119, 6, 0.08);
        border: 1px solid rgba(217, 119, 6, 0.15);
        border-radius: 999px;
        padding: 0.15rem 0.5rem;
        font-size: 0.7rem;
        color: var(--accent-amber);
        margin-right: 0.4rem;
        margin-top: 0.4rem;
    }

    /* ══════════════════════════════════════════════════════════
       CHAT MESSAGES
       ══════════════════════════════════════════════════════════ */
    .stChatMessage {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.85rem !important;
        margin-bottom: 0.6rem !important;
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-normal);
    }

    .stChatMessage:hover {
        box-shadow: var(--shadow-md) !important;
        border-color: var(--border-accent) !important;
    }

    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: var(--text-primary) !important;
        line-height: 1.65;
    }

    /* ══════════════════════════════════════════════════════════
       CHAT INPUT
       ══════════════════════════════════════════════════════════ */
    .stChatInput > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
        transition: border-color var(--transition-fast);
    }

    .stChatInput > div:focus-within {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.1) !important;
    }

    .stChatInput textarea {
        color: var(--text-primary) !important;
    }

    /* ══════════════════════════════════════════════════════════
       FORM INPUTS — COMPACT
       ══════════════════════════════════════════════════════════ */
    .stTextInput > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.3rem 0.6rem !important;
        min-height: 36px !important;
        max-height: 40px !important;
    }

    .stTextInput > div > div:focus-within {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.1) !important;
    }

    .stTextInput input {
        font-size: 0.9rem !important;
        padding: 0.25rem 0.4rem !important;
        color: var(--text-primary) !important;
    }

    .stTextInput label {
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }

    /* ══════════════════════════════════════════════════════════
       BUTTONS
       ══════════════════════════════════════════════════════════ */
    .stButton > button {
        background: var(--gradient-hero) !important;
        color: #fff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.4rem 1.2rem !important;
        transition: all var(--transition-fast) !important;
        box-shadow: var(--shadow-button) !important;
        font-size: 0.88rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(217, 119, 6, 0.3) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ══════════════════════════════════════════════════════════
       TABS
       ══════════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 0.2rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--bg-glass) !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-subtle) !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
        transition: all var(--transition-fast) !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(217, 119, 6, 0.08) !important;
        color: var(--accent-amber) !important;
        border-color: var(--border-accent) !important;
        font-weight: 600 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--accent-gold) !important;
    }

    /* ══════════════════════════════════════════════════════════
       EXPANDER
       ══════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: var(--bg-warm) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
    }

    /* ══════════════════════════════════════════════════════════
       AUDIO WIDGETS
       ══════════════════════════════════════════════════════════ */
    .stAudio audio {
        width: 100%;
        border-radius: var(--radius-sm);
    }

    .stAudioInput > div {
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
        background: var(--bg-secondary) !important;
    }

    /* ══════════════════════════════════════════════════════════
       FILE UPLOADER
       ══════════════════════════════════════════════════════════ */
    .stFileUploader > div {
        border: 2px dashed var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
        background: var(--bg-warm) !important;
        transition: border-color var(--transition-fast);
    }

    .stFileUploader > div:hover {
        border-color: var(--accent-gold) !important;
    }

    /* ══════════════════════════════════════════════════════════
       LOGIN FORM WRAPPER
       ══════════════════════════════════════════════════════════ */
    .login-wrapper {
        max-width: 380px;
        margin: 0.5rem auto;
        padding: 1.5rem;
        background: var(--gradient-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }

    /* ══════════════════════════════════════════════════════════
       SPINNER & STATUS
       ══════════════════════════════════════════════════════════ */
    .stSpinner > div {
        border-color: var(--accent-gold) transparent transparent transparent !important;
    }

    .stAlert {
        border-radius: var(--radius-sm) !important;
    }

    /* ══════════════════════════════════════════════════════════
       SCROLLBAR
       ══════════════════════════════════════════════════════════ */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* ══════════════════════════════════════════════════════════
       RESPONSIVE
       ══════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .hero-title { font-size: 1.6rem; }
        .hero-subtitle { font-size: 0.85rem; }
        .login-wrapper { padding: 1.2rem; margin: 0.75rem; }
    }

    /* ══════════════════════════════════════════════════════════
       LOADING ANIMATION
       ══════════════════════════════════════════════════════════ */
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 10px rgba(217, 119, 6, 0.05); }
        50% { box-shadow: 0 0 25px rgba(217, 119, 6, 0.12); }
    }

    .processing-indicator {
        animation: pulse-glow 2s ease-in-out infinite;
        border: 1px solid var(--border-accent);
        border-radius: var(--radius-md);
        padding: 0.8rem;
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.85rem;
        background: var(--bg-warm);
    }

    /* ══════════════════════════════════════════════════════════
       WELCOME CARD
       ══════════════════════════════════════════════════════════ */
    .welcome-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        text-align: center;
        margin: 0.75rem 0;
        box-shadow: var(--shadow-md);
    }

    .welcome-card h3 {
        color: var(--accent-amber);
        margin-bottom: 0.4rem;
        font-size: 1.2rem;
    }

    .welcome-card .bambara-welcome {
        color: var(--accent-gold);
        font-style: italic;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
    }

    .welcome-card p {
        color: var(--text-secondary);
        line-height: 1.55;
        font-size: 0.88rem;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin-top: 1.2rem;
    }

    .feature-item {
        background: var(--bg-warm);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1rem 0.75rem;
        text-align: center;
        transition: all var(--transition-normal);
    }

    .feature-item:hover {
        border-color: var(--border-accent);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .feature-icon {
        font-size: 1.75rem;
        margin-bottom: 0.35rem;
    }

    .feature-label {
        font-size: 0.78rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .feature-bambara {
        font-size: 0.68rem;
        color: var(--accent-gold);
        font-style: italic;
        margin-top: 0.15rem;
    }

    /* ══════════════════════════════════════════════════════════
       EQUITY BANNER
       ══════════════════════════════════════════════════════════ */
    .equity-banner {
        background: linear-gradient(135deg, #fffbf0 0%, #fef3c7 50%, #fde68a 100%);
        border: 1px solid rgba(217, 119, 6, 0.2);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }

    .equity-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--accent-amber);
        margin-bottom: 0.3rem;
    }

    .equity-text {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }

    .equity-bambara {
        font-size: 0.75rem;
        color: var(--accent-gold);
        font-style: italic;
        margin-top: 0.3rem;
    }
    </style>
    """


def get_login_css() -> str:
    """Return CSS specifically for the login page — subtle warm accents."""
    return """
    <style>
    .login-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    }

    .login-bg::before,
    .login-bg::after {
        content: '';
        position: absolute;
        border-radius: 50%;
        filter: blur(100px);
        opacity: 0.12;
        animation: drift 10s ease-in-out infinite alternate;
    }

    .login-bg::before {
        width: 350px;
        height: 350px;
        background: #f59e0b;
        top: -80px;
        right: -80px;
    }

    .login-bg::after {
        width: 250px;
        height: 250px;
        background: #d97706;
        bottom: -30px;
        left: -30px;
        animation-delay: 5s;
    }

    @keyframes drift {
        0% { transform: translate(0, 0) scale(1); }
        100% { transform: translate(20px, 15px) scale(1.05); }
    }
    </style>
    """
