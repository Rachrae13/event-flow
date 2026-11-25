"""
EVENTFLOW - Futuristic Glassmorphism Design System & Cyber Theme
Provides custom CSS, styling tokens, and layout primitives.
"""

import streamlit as st

def apply_custom_theme():
    """Injects high-end dark glassmorphism styling into Streamlit."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-primary: #070B14;
        --bg-secondary: #0D1527;
        --bg-card: rgba(15, 23, 42, 0.72);
        --bg-card-hover: rgba(22, 34, 61, 0.85);
        --accent-cyan: #00F2FE;
        --accent-blue: #38BDF8;
        --accent-indigo: #6366F1;
        --accent-purple: #8B5CF6;
        --accent-pink: #EC4899;
        --accent-emerald: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #F43F5E;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --border-glass: rgba(56, 189, 248, 0.16);
        --border-glass-hover: rgba(56, 189, 248, 0.4);
        --glow-cyan: 0 0 25px rgba(0, 242, 254, 0.22);
        --glow-purple: 0 0 25px rgba(139, 92, 246, 0.22);
    }

    /* Core Application Canvas */
    .stApp {
        background: 
            radial-gradient(ellipse 90% 60% at 50% -20%, rgba(30, 58, 138, 0.35), transparent 70%),
            radial-gradient(circle 500px at 10% 20%, rgba(139, 92, 246, 0.12), transparent 80%),
            radial-gradient(circle 600px at 90% 75%, rgba(0, 242, 254, 0.1), transparent 85%),
            #060A14 !important;
        color: var(--text-primary);
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Block Container */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1560px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090E1A 0%, #0D1629 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.45);
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        display: none;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0;
    }

    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 750 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.025em;
    }

    p, span, label {
        color: #CBD5E1;
    }

    /* Glass Cards */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.28);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    .glass-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-glass-hover);
        transform: translateY(-3px);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.36), var(--glow-cyan);
    }

    /* Metric Cards */
    .metric-box {
        background: linear-gradient(145deg, rgba(16, 26, 46, 0.85), rgba(11, 18, 33, 0.95));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        padding: 20px 22px;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }
    .metric-box:hover {
        border-color: rgba(0, 242, 254, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 242, 254, 0.15);
    }
    .metric-icon-wrap {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 12px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .metric-title {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 2.1rem;
        font-weight: 850;
        color: #F8FAFC;
        line-height: 1.1;
        font-feature-settings: "tnum";
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(125deg, rgba(26, 54, 93, 0.6) 0%, rgba(49, 27, 98, 0.45) 50%, rgba(13, 21, 39, 0.75) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 24px;
        padding: 32px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.35);
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        top: -60%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(0, 242, 254, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.28);
        color: #38BDF8;
        font-size: 0.75rem;
        font-weight: 750;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-badge-pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00F2FE;
        box-shadow: 0 0 10px #00F2FE;
        animation: pulseLive 1.8s infinite;
    }

    @keyframes pulseLive {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.3); }
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 900;
        background: linear-gradient(135deg, #FFFFFF 30%, #BAE6FD 70%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        color: #CBD5E1;
        font-size: 1.02rem;
        line-height: 1.55;
        max-width: 900px;
        margin: 0;
    }

    /* Badges & Pills */
    .neon-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .pill-cyan { background: rgba(0, 242, 254, 0.12); color: #38BDF8; border: 1px solid rgba(0, 242, 254, 0.25); }
    .pill-purple { background: rgba(139, 92, 246, 0.12); color: #C084FC; border: 1px solid rgba(139, 92, 246, 0.25); }
    .pill-emerald { background: rgba(16, 189, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 189, 129, 0.25); }
    .pill-rose { background: rgba(244, 63, 94, 0.12); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.25); }
    .pill-amber { background: rgba(245, 158, 11, 0.12); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.25); }

    /* Button Styling */
    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #1E40AF 0%, #4338CA 50%, #6D28D9 100%) !important;
        border: 1px solid rgba(147, 197, 253, 0.28) !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
        padding: 0.62rem 1.35rem !important;
        box-shadow: 0 4px 18px rgba(30, 64, 175, 0.3) !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(0, 242, 254, 0.6) !important;
        box-shadow: 0 8px 24px rgba(30, 64, 175, 0.45), 0 0 16px rgba(0, 242, 254, 0.3) !important;
    }

    /* Input & Select Fields */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTimeInput input, .stTextArea textarea {
        background: #0E1729 !important;
        color: #F8FAFC !important;
        border: 1px solid #273752 !important;
        border-radius: 12px !important;
        padding: 0.55rem 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.25) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background: #0E1729 !important;
        color: #F8FAFC !important;
        border: 1px solid #273752 !important;
        border-radius: 12px !important;
    }

    /* Dataframe & Tables */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        background: #0B1323 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(14, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.12);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        color: #94A3B8;
        font-weight: 650;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.4), rgba(124, 58, 237, 0.4)) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }

    /* Section Header */
    .section-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 20px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.12);
    }
    .section-head-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Activity Item */
    .activity-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 13px 16px;
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(56, 189, 248, 0.08);
        border-radius: 12px;
        margin-bottom: 9px;
        transition: all 0.2s ease;
    }
    .activity-row:hover {
        background: rgba(22, 34, 61, 0.75);
        border-color: rgba(56, 189, 248, 0.25);
        transform: translateX(4px);
    }
    .activity-info {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .activity-avatar {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.85rem;
    }
    .activity-name {
        font-weight: 700;
        color: #F8FAFC;
        font-size: 0.92rem;
    }
    .activity-meta {
        font-size: 0.77rem;
        color: #94A3B8;
    }
    </style>
    """, unsafe_allow_html=True)

def get_plotly_dark_theme():
    """Returns standard Plotly layout parameters matching EVENTFLOW cyber theme."""
    return {
        "paper_bgcolor": "rgba(11, 19, 35, 0.0)",
        "plot_bgcolor": "rgba(11, 19, 35, 0.0)",
        "font": {"color": "#CBD5E1", "family": "Plus Jakarta Sans, sans-serif"},
        "margin": {"l": 20, "r": 20, "t": 35, "b": 20},
        "xaxis": {
            "gridcolor": "rgba(56, 189, 248, 0.08)",
            "zerolinecolor": "rgba(56, 189, 248, 0.15)",
            "tickfont": {"color": "#94A3B8"}
        },
        "yaxis": {
            "gridcolor": "rgba(56, 189, 248, 0.08)",
            "zerolinecolor": "rgba(56, 189, 248, 0.15)",
            "tickfont": {"color": "#94A3B8"}
        }
    }
