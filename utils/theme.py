"""
theme.py - Shared colorful styling for the AI Carpool Matching System.
Import `inject_css()` at the top of every page and use `metric_card()`
for vibrant gradient KPI tiles instead of the plain st.metric().
"""

import streamlit as st

PALETTE = {
    "purple": ("#7F5AF0", "#A78BFA"),
    "pink":   ("#F5576C", "#F093FB"),
    "blue":   ("#4FACFE", "#00F2FE"),
    "green":  ("#43E97B", "#38F9D7"),
    "orange": ("#FA8231", "#FED330"),
    "teal":   ("#0BC5C1", "#12D8FA"),
    "red":    ("#FF6B6B", "#FFA36C"),
    "indigo": ("#667EEA", "#764BA2"),
}


def inject_css():
    st.markdown("""
    <style>
        /* ---- Import a nicer font ---- */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

        /* ---- App background: soft animated-feel gradient ---- */
        .stApp {
            background: linear-gradient(135deg, #F0F4FF 0%, #FDF2FF 50%, #F0FBFF 100%);
        }

        /* ---- Main content block ---- */
        .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2E1065 0%, #6D28D9 55%, #BE185D 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #F8F5FF !important;
        }
        section[data-testid="stSidebar"] a {
            border-radius: 10px;
            padding: 6px 10px !important;
            margin-bottom: 2px;
            transition: background 0.15s ease;
        }
        section[data-testid="stSidebar"] a:hover {
            background: rgba(255,255,255,0.15) !important;
        }
        section[data-testid="stSidebar"] button {
            background: linear-gradient(90deg,#F5576C,#F093FB) !important;
            color: white !important;
            border: none !important;
            font-weight: 600;
            border-radius: 10px !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.25) !important;
        }

        /* ---- Headings ---- */
        h1 {
            background: linear-gradient(90deg,#7F5AF0,#F5576C,#FA8231);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        h2 { color: #4C1D95 !important; font-weight: 700 !important; }
        h3 { color: #6D28D9 !important; font-weight: 700 !important; }
        p, .stCaption, [data-testid="stCaptionContainer"] { color: #52527A; }

        /* ---- Buttons ---- */
        .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
            background: linear-gradient(90deg,#7F5AF0,#F5576C);
            color: white !important;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.55em 1.3em;
            box-shadow: 0 4px 12px rgba(127,90,240,0.28);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 8px 20px rgba(245,87,108,0.35);
        }
        .stButton>button:disabled {
            background: linear-gradient(90deg,#C7C7D9,#DADAE8) !important;
            color: #8888A0 !important;
            box-shadow: none;
        }

        /* ---- Tabs ---- */
        div[data-baseweb="tab-list"] {
            gap: 6px;
            background: #F3F0FF;
            padding: 6px;
            border-radius: 14px;
        }
        button[data-baseweb="tab"] {
            border-radius: 10px;
            font-weight: 700;
            color: #6D28D9;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(90deg,#7F5AF0,#F5576C) !important;
            color: white !important;
        }

        /* ---- Containers / cards ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid #ECE9FB !important;
            box-shadow: 0 4px 16px rgba(109,40,217,0.08);
            background: #FFFFFF;
            padding: 4px;
        }

        /* ---- Inputs ---- */
        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        .stDateInput input, .stTimeInput input {
            border-radius: 10px !important;
            border: 1.5px solid #E4DEFB !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #7F5AF0 !important;
            box-shadow: 0 0 0 2px rgba(127,90,240,0.15) !important;
        }
        div[data-baseweb="select"] > div {
            border-radius: 10px !important;
            border: 1.5px solid #E4DEFB !important;
        }
        .stSlider [data-baseweb="slider"] div div div {
            background: linear-gradient(90deg,#7F5AF0,#F5576C) !important;
        }

        /* ---- Expander ---- */
        details {
            border-radius: 12px !important;
            border: 1px solid #ECE9FB !important;
            background: #FAF9FF;
        }
        summary { font-weight: 600; color: #4C1D95 !important; }

        /* ---- Alerts ---- */
        div[data-testid="stAlertContainer"] {
            border-radius: 12px !important;
        }

        /* ---- Metrics (native st.metric) ---- */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg,#7F5AF0,#A78BFA);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 14px rgba(127,90,240,0.25);
        }
        div[data-testid="stMetric"] label, div[data-testid="stMetric"] div {
            color: white !important;
        }

        /* ---- Dataframe ---- */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #ECE9FB;
        }

        /* ---- Metric card (custom) ---- */
        .metric-card {
            border-radius: 16px;
            padding: 18px 20px;
            color: white;
            box-shadow: 0 6px 18px rgba(0,0,0,0.15);
            margin-bottom: 6px;
        }
        .metric-card .m-label {
            font-size: 0.85rem;
            opacity: 0.92;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .metric-card .m-value {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.2;
        }
        .metric-card .m-delta {
            font-size: 0.8rem;
            opacity: 0.88;
        }

        /* ---- Badges ---- */
        .badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            color: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }

        /* ---- Hero banner (login page) ---- */
        .hero-banner {
            background: linear-gradient(120deg,#7F5AF0 0%,#F5576C 55%,#FA8231 100%);
            border-radius: 22px;
            padding: 42px 30px;
            text-align: center;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(127,90,240,0.30);
        }
        .hero-banner h1 {
            -webkit-text-fill-color: white !important;
            background: none !important;
            font-size: 2.4rem !important;
            margin-bottom: 6px;
        }
        .hero-banner p {
            color: #F5F0FF !important;
            font-size: 1.05rem;
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label, value, icon="", color="purple", delta=None, col=None):
    """Render a single colorful gradient KPI card. Pass a streamlit column
    object via `col` to place it, otherwise renders inline."""
    c1, c2 = PALETTE.get(color, PALETTE["purple"])
    delta_html = f"<div class='m-delta'>{delta}</div>" if delta else ""
    html = f"""
    <div class="metric-card" style="background: linear-gradient(135deg,{c1},{c2});">
        <div class="m-label">{icon} {label}</div>
        <div class="m-value">{value}</div>
        {delta_html}
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)


def badge(text, color="purple"):
    c1, c2 = PALETTE.get(color, PALETTE["purple"])
    return f"<span class='badge' style='background:linear-gradient(90deg,{c1},{c2})'>{text}</span>"
