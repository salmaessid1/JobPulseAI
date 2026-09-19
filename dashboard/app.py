# dashboard/app.py
# JobPulseAI – Dashboard Professionnel v5.2 (design "MediCore" 2026)
# Sidebar : scroll unique + organisation + espaces
# >>> Seule la fonction apply_css() (+ la palette CHART_COLORWAY utilisée pour les graphes)
#     a été retravaillée pour matcher le style "MediCore" moderne. Aucun HTML/logique n'a été modifié.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
import sys
import time
import io
import numpy as np
import matplotlib.pyplot as plt
import random
import concurrent.futures
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import traceback
import urllib.request
import urllib.error
import ssl

# Contexte SSL pour développement local
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

# Opener SANS proxy ET avec SSL configuré
_no_proxy_opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    urllib.request.HTTPSHandler(context=_ssl_context),
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ============================================================
# CONFIGURATION & THÈME
# ============================================================
# Lecture robuste du secret (compatible toutes versions Streamlit)
# ⚠️ URL FORCÉE EN DUR (solution définitive)
API_BASE_URL = "https://jobpulseai-ux5q.onrender.com"
print(f"🔗 API_BASE_URL = {API_BASE_URL}")
APP_VERSION = "5.2"


    
defaults = {
    "dark_mode": True,
    "cv_profile": None,
    "gap_result": None,
    "chat_history": [],
    "new_jobs_count": 0,
    "match_result": None,
    "auto_refresh": False,
    "current_page": "🏠 Accueil",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.set_page_config(
    page_title="JobPulseAI – Career Intelligence Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
import urllib.request
import urllib.error
import ssl

# Désactiver la vérification SSL pour localhost (dev uniquement)
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

# Opener sans proxy
_no_proxy_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
# ============================================================
# DESIGN SYSTEM 2026 — "MediCore" — CSS only
# ============================================================
def apply_css(dark=True):
    if dark:
        tokens = {
            # Fond très sombre, bleu-nuit profond (comme MediCore)
            "bg-1": "#07070f", "bg-2": "#0a0b1c", "bg-3": "#0e0f26",
            "surface": "rgba(19, 20, 41, 0.72)",
            "surface-solid": "#12132b",
            "surface-2": "#171935",
            "border": "rgba(255,255,255,0.06)",
            "border-strong": "rgba(139, 92, 246, 0.35)",
            "text-1": "#f5f5fb", "text-2": "#9a9ab8", "text-3": "#65658a",
            "accent-1": "#8b5cf6", "accent-2": "#ec4899", "accent-3": "#3b82f6",
            "success": "#22c55e", "warning": "#f5a524", "danger": "#f43f5e",
            "sidebar-bg": "#0a0b1f",
        }
    else:
        tokens = {
            "bg-1": "#f6f6fb", "bg-2": "#f0f1f9", "bg-3": "#e9ebf6",
            "surface": "rgba(255, 255, 255, 0.82)",
            "surface-solid": "#ffffff",
            "surface-2": "#f4f4fb",
            "border": "rgba(15, 23, 42, 0.08)",
            "border-strong": "rgba(139, 92, 246, 0.28)",
            "text-1": "#12131f", "text-2": "#525268", "text-3": "#8a8aa3",
            "accent-1": "#7c3aed", "accent-2": "#db2777", "accent-3": "#2563eb",
            "success": "#16a34a", "warning": "#b45309", "danger": "#dc2626",
            "sidebar-bg": "#ffffff",
        }

    css_vars = "\n".join([f"--{k}: {v};" for k, v in tokens.items()])

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

        :root {{
            {css_vars}
            --radius-xl: 26px;
            --radius-lg: 20px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --shadow-soft: 0 12px 32px rgba(3, 4, 16, 0.45);
            --shadow-pop: 0 18px 44px rgba(139, 92, 246, 0.22);
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        * {{
            scrollbar-width: thin;
            scrollbar-color: var(--border-strong) transparent;
        }}
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}

        .stApp {{
            background:
                radial-gradient(900px 480px at 12% -8%, rgba(139,92,255,0.18), transparent 60%),
                radial-gradient(760px 420px at 100% 0%, rgba(236,72,153,0.10), transparent 55%),
                linear-gradient(165deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-3) 100%);
            background-attachment: fixed;
            color: var(--text-1);
        }}

        .stApp::before {{
            content: '';
            position: fixed; inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.02'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
        }}
        .stApp > div {{ position: relative; z-index: 1; }}

        /* ========== SIDEBAR "MediCore" : scroll unique + organisation ========== */
        section[data-testid="stSidebar"] {{
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border);
            overflow-x: hidden !important;
            overflow-y: auto !important;
            height: 100vh !important;
        }}

        section[data-testid="stSidebar"] > div {{
            overflow: visible !important;
            height: auto !important;
            min-height: 100%;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
            overflow: visible !important;
            padding: 1.25rem 1rem 2.2rem 1rem !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: var(--text-1);
            box-sizing: border-box;
        }}

        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stCaption {{
            color: var(--text-2);
        }}

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.5rem !important;
        }}

        section[data-testid="stSidebar"] .element-container {{
            margin-bottom: 0.15rem !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {{
            margin-bottom: 0.15rem !important;
        }}

        /* Labels de section — petites majuscules discrètes */
        .sidebar-section-label {{
            font-size: 0.66rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-3) !important;
            margin: 1rem 0 0.5rem 0.2rem !important;
            display: block;
        }}

        /* Séparateurs fins */
        .sidebar-divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border) 15%, var(--border) 85%, transparent);
            margin: 0.9rem 0 0.7rem 0;
        }}

        /* Navigation — pilule pleine violette à l'état actif, comme MediCore */
        section[data-testid="stSidebar"] div[role="radiogroup"] {{
            gap: 4px !important;
            display: flex;
            flex-direction: column;
            margin-bottom: 0.3rem;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            background: transparent;
            border-radius: var(--radius-sm);
            padding: 9px 12px !important;
            transition: all 0.18s ease;
            border: 1px solid transparent;
            width: 100%;
            min-height: 0 !important;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: rgba(139, 92, 246, 0.10);
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
            background: linear-gradient(135deg, var(--accent-1), #7c3aed);
            box-shadow: 0 8px 20px rgba(139,92,246,0.35);
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{
            color: #ffffff !important;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {{
            font-weight: 600 !important;
            font-size: 0.86rem !important;
            margin: 0 !important;
        }}

        /* Bloc métriques "En un coup d'œil" — carte flat foncée */
        .sidebar-metrics {{
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 0.75rem 0.95rem;
            margin: 0.25rem 0 0.4rem 0;
        }}
        .sidebar-metrics .metric {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.34rem 0;
            border-bottom: 1px dashed var(--border);
        }}
        .sidebar-metrics .metric:last-child {{ border-bottom: none; }}
        .sidebar-metrics .label {{ color: var(--text-2); font-size: 0.78rem; }}
        .sidebar-metrics .value {{ font-weight: 700; color: var(--text-1); font-size: 0.88rem; }}

        /* Toggles */
        section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {{
            font-size: 0.84rem !important;
            font-weight: 500 !important;
        }}
        section[data-testid="stSidebar"] label[data-baseweb="checkbox"] {{
            transform: scale(0.88);
            transform-origin: left center;
        }}
        section[data-testid="stSidebar"] div[data-testid="stToggle"] {{
            margin-bottom: 0.15rem !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stToggle"] label div[data-checked="true"],
        section[data-testid="stSidebar"] [role="switch"][aria-checked="true"] {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2)) !important;
        }}

        /* Boutons sidebar — flat, contour discret, fond plein au survol */
        section[data-testid="stSidebar"] .stButton > button {{
            background: var(--surface-2);
            color: var(--text-1);
            border: 1px solid var(--border);
            box-shadow: none;
            font-weight: 600;
            padding: 0.5rem 1rem;
            margin-top: 0.15rem;
            border-radius: var(--radius-sm);
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white;
            border-color: transparent;
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(139,92,246,0.28);
        }}

        /* Footer sidebar */
        .sidebar-footer {{
            margin-top: 1.1rem;
            padding-top: 0.75rem;
            border-top: 1px solid var(--border);
            font-size: 0.68rem;
            color: var(--text-3);
            display: flex;
            flex-direction: column;
            gap: 0.22rem;
        }}

        /* ========== HEADER PRINCIPAL ========== */
        .main-header {{
            font-family: 'Sora', sans-serif;
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--text-1);
            padding: 0.2rem 0 0.9rem 0;
            margin-bottom: 1.4rem;
            display: flex; align-items: center; gap: 0.6rem;
            border-bottom: 1px solid var(--border);
            position: relative;
        }}
        .main-header::after {{
            content: '';
            position: absolute; left: 0; bottom: -1px;
            width: 96px; height: 3px; border-radius: 3px;
            background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
        }}

        /* ========== CARTES KPI — flat, icônes colorées type MediCore ========== */
        .metric-card {{
            background: var(--surface-solid);
            border: 1px solid var(--border);
            border-radius: var(--radius-xl);
            padding: 1.3rem 1.5rem;
            box-shadow: var(--shadow-soft);
            margin-bottom: 0.9rem;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
            position: relative;
            overflow: hidden;
        }}
        .metric-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-strong);
            box-shadow: var(--shadow-pop);
        }}
        .metric-icon {{
            width: 44px; height: 44px;
            border-radius: 13px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.25rem;
            background: color-mix(in srgb, var(--card-accent, var(--accent-1)) 16%, transparent);
            margin-bottom: 0.8rem;
        }}
        .metric-label {{
            font-size: 0.76rem; color: var(--text-2);
            text-transform: uppercase; letter-spacing: 0.07em;
            font-weight: 600; margin-bottom: 0.3rem;
        }}
        .metric-value {{
            font-family: 'Sora', sans-serif;
            font-size: 2.05rem; font-weight: 700;
            color: var(--text-1);
            line-height: 1.1;
        }}
        .metric-trend-up {{ color: var(--success); font-weight: 700; }}
        .metric-trend-down {{ color: var(--danger); font-weight: 700; }}

        /* Badges pilules */
        .badge-success {{
            background: color-mix(in srgb, var(--success) 16%, transparent);
            color: var(--success);
            border: 1px solid color-mix(in srgb, var(--success) 35%, transparent);
            padding: 0.24rem 0.85rem; border-radius: 999px;
            font-size: 0.75rem; font-weight: 700;
        }}
        .badge-warning {{
            background: color-mix(in srgb, var(--warning) 16%, transparent);
            color: var(--warning);
            border: 1px solid color-mix(in srgb, var(--warning) 35%, transparent);
            padding: 0.24rem 0.85rem; border-radius: 999px;
            font-size: 0.75rem; font-weight: 700;
        }}
        .badge-danger {{
            background: color-mix(in srgb, var(--danger) 16%, transparent);
            color: var(--danger);
            border: 1px solid color-mix(in srgb, var(--danger) 35%, transparent);
            padding: 0.24rem 0.85rem; border-radius: 999px;
            font-size: 0.75rem; font-weight: 700;
        }}

        /* Boutons principaux — dégradé violet → rose, comme "Upgrade Now" MediCore */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white; border: none;
            border-radius: var(--radius-sm);
            padding: 0.64rem 1.6rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            transition: all 0.22s ease;
            box-shadow: 0 8px 20px rgba(139,92,246,0.3);
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(236,72,153,0.35);
            filter: brightness(1.05);
        }}

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {{
            background-color: var(--surface-solid) !important;
            color: var(--text-1) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
        }}
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--accent-1) !important;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.18) !important;
        }}

        .st-expander, .stAlert, div[data-testid="stExpander"] {{
            background: var(--surface) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            box-shadow: var(--shadow-soft) !important;
        }}

        .stMarkdown, p, span, label {{ color: var(--text-1); }}
        .stCaption, [data-testid="stCaptionContainer"] {{ color: var(--text-3) !important; }}

        .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
        .js-plotly-plot .plotly .cartesianlayer {{ background: transparent !important; }}

        div[data-testid="stMetric"] {{
            background: var(--surface-solid);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1.05rem 1.25rem;
        }}
        div[data-testid="stMetricLabel"] {{ color: var(--text-2) !important; }}
        div[data-testid="stMetricValue"] {{ color: var(--text-1) !important; font-family: 'Sora', sans-serif; }}

        .comp-table {{ border-collapse: collapse; width: 100%; border-radius: var(--radius-md); overflow: hidden; }}
        .comp-table th, .comp-table td {{ border: 1px solid var(--border); padding: 10px 12px; text-align: left; color: var(--text-1); }}
        .comp-table th {{ background: linear-gradient(135deg, var(--accent-1), var(--accent-2)); color: white; font-weight: 700; }}
        .comp-table tr:nth-child(even) {{ background: var(--surface-2); }}

        .suggestion-card {{
            background: var(--surface-solid);
            border: 1px solid var(--border);
            border-left: 4px solid var(--accent-1);
            border-radius: var(--radius-md);
            padding: 1rem;
            margin-bottom: 0.6rem;
        }}
    </style>
    """, unsafe_allow_html=True)

apply_css(st.session_state.dark_mode)

# ============================================================
# FONCTIONS API (inchangées)
# ============================================================
import subprocess

def _fetch_silent(endpoint, timeout=30):
    """Appelle l'API via curl.exe (contourne les problèmes de proxy)."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        result = subprocess.run(
            ["curl.exe", "-s", "-m", str(timeout), url],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
        if result.returncode != 0:
            print(f"🔴 curl erreur [{endpoint}] : {result.stderr}")
            return None
        data = result.stdout.strip()
        if not data:
            return None
        return json.loads(data)
    except Exception as e:
        print(f"🔴 _fetch_silent [{endpoint}] : {type(e).__name__} - {e}")
        return None

def api_call(method, endpoint, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        # Cas multipart (upload fichier) : utiliser requests sans proxy
        if "files" in kwargs:
            files = kwargs["files"]
            resp = requests.post(
                url, files=files, timeout=30,
                proxies={"http": None, "https": None},
            )
            resp.raise_for_status()
            return resp.json()

        # Cas JSON : utiliser urllib sans proxy
        data = None
        headers = {}
        if "json" in kwargs:
            data = json.dumps(kwargs["json"]).encode('utf-8')
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers)
        with _no_proxy_opener.open(req, timeout=20) as resp:
            return json.loads(resp.read().decode('utf-8'))

    except urllib.error.HTTPError as e:
        print(f"🔴 HTTP Error {e.code} : {e.reason}")
        st.error(f"❌ Erreur HTTP {e.code}")
        return None
    except urllib.error.URLError as e:
        print(f"🔴 URL Error : {e.reason}")
        st.error(f"❌ Connexion impossible : {e.reason}")
        return None
    except Exception as e:
        print(f"🔴 Erreur : {type(e).__name__} - {e}")
        st.error(f"❌ Erreur : {e}")
        return None

@st.cache_data(ttl=60, show_spinner=False)
def get_global_stats():
    return _fetch_silent("/stats/global")

@st.cache_data(ttl=60, show_spinner=False)
def get_top_skills(limit=10):
    return _fetch_silent(f"/stats/skills/top?limit={limit}")

@st.cache_data(ttl=60, show_spinner=False)
def get_salary_distribution():
    return _fetch_silent("/stats/salary/distribution")

@st.cache_data(ttl=60, show_spinner=False)
def get_top_companies(limit=10):
    return _fetch_silent(f"/stats/companies/top?limit={limit}")

@st.cache_data(ttl=60, show_spinner=False)
def get_top_jobs(limit=10):
    return _fetch_silent(f"/stats/jobs/top?limit={limit}")

@st.cache_data(ttl=60, show_spinner=False)
def get_experience_levels():
    return _fetch_silent("/stats/experience/levels")

@st.cache_data(ttl=60, show_spinner=False)
def get_market_overview():
    endpoints = {
        "companies": "/stats/companies/top?limit=10",
        "jobs": "/stats/jobs/top?limit=10",
        "salary": "/stats/salary/distribution",
        "levels": "/stats/experience/levels",
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {key: executor.submit(_fetch_silent, ep) for key, ep in endpoints.items()}
        return {key: f.result() for key, f in futures.items()}

def analyze_cv_api(file_bytes, filename):
    files = {"file": (filename, file_bytes, "application/pdf")}
    return api_call("POST", "/cv/upload", files=files)

def match_api(cv_text, job_text):
    payload = {"cv_text": cv_text, "job_text": job_text}
    return api_call("POST", "/matching/", json=payload, timeout=12)

def skill_gap_api(profile, job_text):
    payload = {"profile": profile, "job_text": job_text}
    return api_call("POST", "/skill-gap/", json=payload, timeout=12)

def recommendations_api(profile, top_n=10):
    payload = {"profile": profile, "top_n": top_n}
    return api_call("POST", "/recommendations/", json=payload, timeout=15)

def salary_api(features):
    return api_call("POST", "/salary/predict", json=features, timeout=10)

def compute_cv_score(profile):
    score = 0
    if profile.get('name') and profile['name'] != 'Inconnu':
        score += 10
    skills = profile.get('skills', [])
    if len(skills) >= 10:
        score += 30
    elif len(skills) >= 5:
        score += 20
    elif len(skills) >= 3:
        score += 10
    domains = profile.get('domains', [])
    if len(domains) >= 3:
        score += 20
    elif len(domains) >= 1:
        score += 10
    seniority = profile.get('seniority', '')
    if seniority in ['senior', 'lead']:
        score += 20
    elif seniority == 'mid':
        score += 10
    else:
        score += 5
    return min(score, 100)

PLOTLY_TEMPLATE = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
CHART_COLORWAY = ["#8b5cf6", "#ec4899", "#3b82f6", "#f5a524", "#f43f5e", "#22c55e"]

def style_fig(fig, height=320):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CHART_COLORWAY,
        font=dict(family="Inter, sans-serif", color="#9a9ab8" if st.session_state.dark_mode else "#525268"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

def generate_radar(profile):
    categorized = profile.get('categorized_skills', {})
    categories = list(categorized.keys())
    values = [len(categorized[cat]) for cat in categories]
    if not categories:
        categories = ['Aucune catégorie']
        values = [0]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Compétences',
        line_color="#8b5cf6",
        fillcolor="rgba(139,92,246,0.25)"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, max(values)+1 if values else 1])
        ),
        showlegend=False
    )
    return style_fig(fig, height=400)

def generate_radar_image(profile):
    categorized = profile.get('categorized_skills', {})
    categories = list(categorized.keys())
    values = [len(categorized[cat]) for cat in categories]
    if not categories:
        categories = ['Aucune']
        values = [0]
    categories += [categories[0]]
    values += [values[0]]
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(categories, values, alpha=0.3, color='#8b5cf6')
    ax.plot(categories, values, marker='o', color='#8b5cf6')
    ax.set_title("Radar des compétences", size=12, pad=20)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()
    return buf

def generate_pdf_report(profile, score, recommendations=None, salary_pred=None):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, alignment=TA_CENTER, spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=16, spaceAfter=6, textColor=colors.HexColor('#8b5cf6'))
    normal_style = styles['Normal']

    story = []
    story.append(Paragraph("📊 Rapport JobPulseAI", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Nom :</b> {profile.get('name', 'Inconnu')}", normal_style))
    story.append(Paragraph(f"<b>Séniorité :</b> {profile.get('seniority', 'Non défini')}", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Score du CV", heading_style))
    story.append(Paragraph(f"<b>{score}/100</b>", normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("🔵🔵🔵🔵🔵🔵🔵⚪⚪⚪ 70% (exemple)", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Compétences extraites", heading_style))
    skills = profile.get('skills', [])
    skills_text = ", ".join(skills) if skills else "Aucune compétence détectée"
    story.append(Paragraph(skills_text, normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Domaines", heading_style))
    domains = profile.get('domains', [])
    domains_text = ", ".join(domains) if domains else "Aucun domaine"
    story.append(Paragraph(domains_text, normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Radar des compétences", heading_style))
    radar_img = generate_radar_image(profile)
    img = Image(radar_img, width=150, height=150)
    img.hAlign = 'CENTER'
    story.append(img)
    story.append(Spacer(1, 12))
    if recommendations:
        story.append(Paragraph("Recommandations d'offres (top 3)", heading_style))
        for i, rec in enumerate(recommendations[:3], 1):
            title = rec.get('title', 'Offre')
            company = rec.get('company', 'Inconnue')
            score_rec = rec.get('score', 0)
            story.append(Paragraph(f"{i}. {title} - {company} (Score: {score_rec}%)", normal_style))
        story.append(Spacer(1, 12))
    if salary_pred:
        story.append(Paragraph("Prédiction de salaire", heading_style))
        pred = salary_pred.get('predicted_salary', 0)
        min_r = salary_pred.get('min_range', 0)
        max_r = salary_pred.get('max_range', 0)
        story.append(Paragraph(f"Estimation : {pred:.2f} USD", normal_style))
        story.append(Paragraph(f"Fourchette : {min_r:.2f} - {max_r:.2f} USD", normal_style))
        story.append(Spacer(1, 12))
    story.append(Spacer(1, 24))
    story.append(Paragraph("---", normal_style))
    story.append(Paragraph("Rapport généré par JobPulseAI © 2026", normal_style))
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# ============================================================
# SIDEBAR (scroll unique + organisation + espaces)
# ============================================================
with st.sidebar:
    # ----- Branding -----
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.65rem; margin-bottom:0.35rem;">
        <div style="width:40px; height:40px; border-radius:11px; flex-shrink:0;
             background:linear-gradient(135deg,#8b5cf6,#ec4899);
             display:flex; align-items:center; justify-content:center;
             font-size:1.2rem; box-shadow:0 6px 16px rgba(139,92,246,0.35);">📊</div>
        <div style="line-height:1.15;">
            <div style="font-family:'Sora',sans-serif; font-weight:800; font-size:1.15rem;
                 background:linear-gradient(135deg,#8b5cf6,#ec4899);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                JobPulseAI
            </div>
            <div style="color:var(--text-3); font-size:0.65rem; letter-spacing:0.07em; font-weight:600;">
                CAREER INTELLIGENCE · v{version}
            </div>
        </div>
    </div>
    """.format(version=APP_VERSION), unsafe_allow_html=True)

    # ----- Statut API -----
    stats = get_global_stats()
    api_ok = stats is not None
    status_color = "#22c55e" if api_ok else "#f43f5e"
    status_label = "API connectée" if api_ok else "API hors ligne"
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.5rem; margin:0.4rem 0 0.6rem 0;">
        <span style="width:8px; height:8px; border-radius:50%; background:{status_color};
             box-shadow:0 0 0 3px {status_color}26; display:inline-block;"></span>
        <span style="font-size:0.75rem; color:var(--text-2); font-weight:500;">{status_label}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ----- Menu -----
    st.markdown('<p class="sidebar-section-label">Menu</p>', unsafe_allow_html=True)
    pages = ["🏠 Accueil", "📈 Marché", "📈 Tendances", "📄 CV", "🤝 Matching",
             "🎯 Recommandations", "💰 Salaire", "📊 Comparateur", "📊 Analyse carrière", "🤖 Assistant", "📄 Rapport"]
    
    current_idx = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
    page = st.radio(
        "Navigation",
        pages,
        index=current_idx,
        label_visibility="collapsed",
        key="nav_radio"
    )
    st.session_state.current_page = page

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ----- Préférences -----
    st.markdown('<p class="sidebar-section-label">Préférences</p>', unsafe_allow_html=True)

    dark_mode = st.toggle("🌙 Mode sombre", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()

    auto_refresh = st.toggle("🔄 Auto-refresh (15s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    if auto_refresh:
        st.caption("📡 Rafraîchissement automatique toutes les 15s.")
        st.markdown('<meta http-equiv="refresh" content="15">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ----- En un coup d'œil -----
    st.markdown('<p class="sidebar-section-label">En un coup d\'œil</p>', unsafe_allow_html=True)

    if stats:
        st.markdown(f"""
        <div class="sidebar-metrics">
            <div class="metric"><span class="label">📋 Offres</span><span class="value">{stats.get('total_jobs', 0):,}</span></div>
            <div class="metric"><span class="label">🧠 Compétences</span><span class="value">{stats.get('unique_skills', 0):,}</span></div>
            <div class="metric"><span class="label">🏢 Entreprises</span><span class="value">{stats.get('unique_companies', 0):,}</span></div>
            <div class="metric"><span class="label">🌍 Taux remote</span><span class="value">{stats.get('remote_percent', 0):.1f}%</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Données indisponibles — vérifie que l'API tourne.", icon="⚠️")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ----- Session -----
    st.markdown('<p class="sidebar-section-label">Session</p>', unsafe_allow_html=True)

    profile = st.session_state.cv_profile
    if profile:
        name = profile.get('name', 'Inconnu')
        skills_count = len(profile.get('skills', []))
        st.markdown(f"""
        <div style="background:var(--surface); border:1px solid var(--border); border-radius:10px;
                    padding:0.7rem 0.9rem; margin:0.25rem 0 0.6rem 0;">
            <div style="font-size:0.72rem; color:var(--text-3); margin-bottom:0.25rem;">📄 CV chargé</div>
            <div style="font-weight:600; font-size:0.92rem;">{name}</div>
            <div style="font-size:0.76rem; color:var(--text-2); margin-top:0.15rem;">{skills_count} compétences</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("Aucun CV chargé")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Reset CV", use_container_width=True, key="reset_cv"):
            st.session_state.cv_profile = None
            st.session_state.gap_result = None
            st.session_state.match_result = None
            st.success("Profil CV réinitialisé")
            st.rerun()
    with col_b:
        if st.button("🧹 Cache", use_container_width=True, key="clear_cache"):
            st.cache_data.clear()
            st.success("Cache vidé")
            st.rerun()

    st.markdown("<div style='height:0.45rem'></div>", unsafe_allow_html=True)

    if st.button("🔄 Actualiser les données", key="refresh_sidebar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # ----- Footer -----
    st.markdown(f"""
    <div class="sidebar-footer">
        <div>🔗 {API_BASE_URL}</div>
        <div>🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <div>v{APP_VERSION}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGES (inchangées)
# ============================================================
def kpi_card(col, icon, label, value, trend=None, trend_dir="up", accent="#8b5cf6"):
    trend_html = ""
    if trend is not None:
        cls = "metric-trend-up" if trend_dir == "up" else "metric-trend-down"
        arrow = "↑" if trend_dir == "up" else "↓"
        trend_html = f'<div><span class="{cls}">{arrow} {trend}</span> <span style="color:var(--text-3); font-size:0.78rem;">vs période précédente</span></div>'
    with col:
        st.markdown(f"""
        <div class="metric-card" style="--card-accent:{accent};">
            <div class="metric-icon" style="color:{accent};">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {trend_html}
        </div>
        """, unsafe_allow_html=True)

def page_accueil():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📊 Tableau de bord – Performance du recrutement</div>', unsafe_allow_html=True)
    st.caption("Comprenez la performance de votre recrutement en temps réel.")

    if st.session_state.get("auto_refresh", False) and random.random() < 0.3:
        st.toast("📢 Une nouvelle offre correspond à votre profil !", icon="🎯")

    stats = get_global_stats()
    if not stats:
        st.warning("Impossible de charger les statistiques.")
        return

    variation = random.randint(-5, 5)
    total_jobs = stats.get('total_jobs', 0) + variation

    col1, col2, col3, col4 = st.columns(4)
    kpi_card(col1, "📊", "Offres actives", f"{total_jobs:,}", f"{variation:+d}%", "up", "#8b5cf6")
    kpi_card(col2, "⏳", "Temps de matching moyen", "7.3 j", "2%", "down", "#3b82f6")
    kpi_card(col3, "✅", "Taux de recommandation", "92%", None, "up", "#22c55e")
    kpi_card(col4, "🤖", "Prédiction IA (acceptation)", "86%", "4%", "up", "#ec4899")

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🎯 Précision du matching IA par département")
        depts = ["Design", "Marketing", "Engineering", "Sales"]
        accuracy = [92.67, 78.5, 85.3, 72.1]
        fig = px.bar(x=accuracy, y=depts, orientation='h',
                     color=accuracy, color_continuous_scale=["#3b82f6", "#8b5cf6"],
                     title="Précision du matching par département")
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)

        st.subheader("🏢 Recrutements par département")
        hires = [28, 35, 42, 18]
        fig2 = px.bar(x=depts, y=hires, color=depts,
                      color_discrete_sequence=CHART_COLORWAY,
                      title="Recrutements par département")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig2, 300), use_container_width=True)

    with col_right:
        st.subheader("🔄 Conversion des candidats")
        stages = ["Shortlistés par IA", "Entretiens", "Offres envoyées", "Offres acceptées"]
        values = [310, 310, 65, 42]
        fig3 = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(color=["#8b5cf6", "#3b82f6", "#ec4899", "#22c55e"])
        ))
        st.plotly_chart(style_fig(fig3, 350), use_container_width=True)

        st.subheader("📈 Distribution des correspondances")
        labels = ['Excellente (92%)', 'Modérée (36%)', 'Bonne (16%)', 'Faible (5%)']
        values = [92.67, 36, 16, 5]
        fig4 = px.pie(values=values, names=labels, hole=0.55,
                      color_discrete_sequence=CHART_COLORWAY)
        st.plotly_chart(style_fig(fig4, 280), use_container_width=True)

def page_marche():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📈 Analyse du marché</div>', unsafe_allow_html=True)

    with st.spinner("Chargement des données du marché..."):
        market = get_market_overview()

    top_companies = market.get("companies")
    top_jobs = market.get("jobs")
    salary_dist = market.get("salary")
    levels = market.get("levels")

    col1, col2 = st.columns(2)
    with col1:
        if top_companies:
            df_companies = pd.DataFrame(top_companies)
            fig = px.bar(df_companies, x='company', y='count', title="Top entreprises",
                         color_discrete_sequence=["#8b5cf6"])
            st.plotly_chart(style_fig(fig), use_container_width=True)
    with col2:
        if top_jobs:
            df_jobs = pd.DataFrame(top_jobs)
            fig = px.bar(df_jobs, x='title', y='count', title="Top métiers",
                         color_discrete_sequence=["#ec4899"])
            st.plotly_chart(style_fig(fig), use_container_width=True)

    if salary_dist and salary_dist.get('salaries'):
        salaries = salary_dist['salaries']
        fig = px.histogram(salaries, nbins=30, title="Distribution des salaires normalisés",
                           color_discrete_sequence=["#3b82f6"])
        st.plotly_chart(style_fig(fig), use_container_width=True)

    if levels:
        fig = px.pie(values=list(levels.values()), names=list(levels.keys()), title="Niveaux d'expérience",
                     color_discrete_sequence=CHART_COLORWAY)
        st.plotly_chart(style_fig(fig), use_container_width=True)
# Dans page_marche()
st.subheader("🏢 Répartition par secteur")
sectors = api_call("GET", "/stats/sectors/distribution")
if sectors:
    df_sectors = pd.DataFrame(sectors)
    fig = px.pie(df_sectors, values='count', names='sector', 
                 title="Offres par secteur", hole=0.4)
    st.plotly_chart(style_fig(fig), use_container_width=True)

st.subheader("💰 Salaire moyen par secteur")
sector_salaries = api_call("GET", "/stats/sectors/salaries")
if sector_salaries:
    df_ss = pd.DataFrame(sector_salaries)
    fig = px.bar(df_ss, x='sector', y='avg_salary', 
                 title="Salaire moyen par secteur")
    st.plotly_chart(style_fig(fig), use_container_width=True)
st.subheader("🌍 Top villes qui recrutent")
locations = api_call("GET", "/stats/locations/top?limit=15")
if locations:
    df_loc = pd.DataFrame(locations)
    fig = px.bar(df_loc, x='count', y='city', orientation='h',
                 title="Top 15 villes", color='count', color_continuous_scale='Blues')
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(style_fig(fig, 450), use_container_width=True)

st.subheader("🏠 Taux de remote par ville")
remote_loc = api_call("GET", "/stats/locations/remote?limit=10")
if remote_loc:
    df_rl = pd.DataFrame(remote_loc)
    fig = px.bar(df_rl, x='city', y='remote_rate',
                 title="Taux de remote par ville (%)")
    st.plotly_chart(style_fig(fig), use_container_width=True)

st.subheader("🔥 Matrice de co-occurrence des compétences")
cooc = api_call("GET", "/stats/skills/cooccurrence?nrows=300")
if cooc and cooc.get('skills'):
    df_cooc = pd.DataFrame(cooc['matrix'], 
                          index=cooc['skills'], 
                          columns=cooc['skills'])
    fig = px.imshow(df_cooc, 
                    color_continuous_scale='Purples',
                    title="Co-occurrence des compétences (Top 15)")
    fig.update_layout(height=600)
    st.plotly_chart(style_fig(fig, 600), use_container_width=True)




def page_tendances():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📈 Tendances du marché</div>', unsafe_allow_html=True)
    st.write("Évolution des salaires, du remote et des compétences dans le temps.")

    @st.cache_data(ttl=300)
    def load_trend_data(nrows=200):
        try:
            df = pd.read_csv("data/raw/postings.csv", nrows=nrows, low_memory=False)
            if 'listed_time' in df.columns:
                df['listed_time'] = pd.to_datetime(df['listed_time'], errors='coerce')
            return df
        except:
            return pd.DataFrame()

    df = load_trend_data(500)
    if df.empty:
        st.warning("Aucune donnée de tendance disponible. Utilisation de données simulées.")
        months = pd.date_range('2023-01', periods=12, freq='M')
        salaries = np.random.normal(80000, 10000, 12) + np.arange(12)*500
        remote = 0.3 + np.arange(12)*0.02
        df_sim = pd.DataFrame({'month': months.strftime('%Y-%m'), 'salary': salaries, 'remote': remote})
        fig = px.line(df_sim, x='month', y='salary', title='Simulation tendance des salaires',
                      color_discrete_sequence=["#8b5cf6"])
        st.plotly_chart(style_fig(fig), use_container_width=True)
        fig2 = px.line(df_sim, x='month', y='remote', title='Simulation tendance remote',
                       color_discrete_sequence=["#ec4899"])
        st.plotly_chart(style_fig(fig2), use_container_width=True)
        return

    date_col = 'listed_time' if 'listed_time' in df.columns else None
    if date_col:
        df = df.dropna(subset=[date_col])
        df = df.sort_values(date_col)
        df['month'] = df[date_col].dt.to_period('M')

        if 'normalized_salary' in df.columns:
            monthly = df.groupby('month')['normalized_salary'].mean().reset_index()
            monthly['month'] = monthly['month'].astype(str)
            fig = px.line(monthly, x='month', y='normalized_salary',
                          title='Évolution du salaire moyen normalisé',
                          labels={'month': 'Mois', 'normalized_salary': 'Salaire moyen'},
                          color_discrete_sequence=["#8b5cf6"])
            st.plotly_chart(style_fig(fig), use_container_width=True)

        if 'remote_allowed' in df.columns:
            remote_over_time = df.groupby('month')['remote_allowed'].mean().reset_index()
            remote_over_time['month'] = remote_over_time['month'].astype(str)
            fig = px.line(remote_over_time, x='month', y='remote_allowed',
                          title='Taux de remote dans le temps',
                          labels={'month': 'Mois', 'remote_allowed': 'Proportion remote'},
                          color_discrete_sequence=["#ec4899"])
            st.plotly_chart(style_fig(fig), use_container_width=True)
    else:
        st.info("Colonne de date non trouvée.")

def page_cv():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📄 Analyse de CV</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choisissez votre CV (PDF)", type=["pdf"])

    if uploaded:
        with st.spinner("📤 Upload et analyse en cours..."):
            file_bytes = uploaded.read()
            result = analyze_cv_api(file_bytes, uploaded.name)
            if result:
                st.success("✅ Analyse terminée !")
                profile = result.get("profile", {})
                st.session_state.cv_profile = profile

                score = compute_cv_score(profile)
                st.metric("📊 Score du CV", f"{score}/100", delta="Qualité du profil")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("👤 Profil")
                    st.write(f"**Nom :** {profile.get('name', 'Inconnu')}")
                    st.write(f"**Séniorité :** {profile.get('seniority', 'Non défini')}")
                    domains = profile.get('domains', [])
                    st.write(f"**Domaines :** {', '.join(domains) if domains else 'Aucun'}")

                with col2:
                    st.subheader("🧠 Compétences")
                    skills = profile.get('skills', [])
                    st.write(f"{len(skills)} compétences trouvées")
                    st.write(", ".join(skills[:20]) + ("..." if len(skills) > 20 else ""))

                st.subheader("📊 Radar des compétences par catégorie")
                fig = generate_radar(profile)
                st.plotly_chart(fig, use_container_width=True)

                if skills:
                    df_skills = pd.DataFrame({"Compétence": skills})
                    fig = px.bar(df_skills.value_counts().reset_index(),
                                 x='Compétence', y='count', title="Top compétences",
                                 color_discrete_sequence=["#8b5cf6"])
                    st.plotly_chart(style_fig(fig), use_container_width=True)

                with st.expander("📤 Exporter le profil"):
                    st.download_button("📥 JSON", data=json.dumps(profile, indent=2),
                                       file_name="cv_profile.json", mime="application/json")
            else:
                st.error("Échec de l'analyse.")

def page_matching():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">🤝 Matching CV / Offre</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        cv_text = st.text_area("📄 Texte de votre CV", height=150, key="cv_input")
    with col2:
        job_text = st.text_area("📋 Description du poste", height=150, key="job_input")

    if st.button("🔍 Analyser le matching", use_container_width=True):
        if cv_text and job_text:
            with st.spinner("Calcul du matching..."):
                result = match_api(cv_text, job_text)
                if result:
                    st.session_state.match_result = result
                else:
                    st.error("Échec du matching (API).")
        else:
            st.warning("Remplissez les deux champs.")

    if st.session_state.match_result:
        result = st.session_state.match_result
        score = result.get('score', 0)
        common = result.get('common_skills', [])
        missing = result.get('missing_skills', [])

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Score (%)"},
            domain={"x": [0,1], "y":[0,1]},
            gauge={
                "axis": {"range": [0,100]},
                "bar": {"color": "#8b5cf6"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0,50], "color": "rgba(244,63,94,0.18)"},
                    {"range": [50,75], "color": "rgba(245,165,36,0.18)"},
                    {"range": [75,100], "color": "rgba(34,197,94,0.18)"}
                ]
            }
        ))
        st.plotly_chart(style_fig(fig), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Compétences communes", len(common))
            st.write(", ".join(common) if common else "Aucune")
        with col2:
            st.metric("Compétences manquantes", len(missing))
            st.write(", ".join(missing) if missing else "Aucune")

        with st.expander("📤 Exporter"):
            st.download_button("📥 JSON", data=json.dumps(result, indent=2),
                               file_name="matching_result.json", mime="application/json")

def page_recommandations():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">🎯 Recommandations d\'offres</div>', unsafe_allow_html=True)

    profile = st.session_state.cv_profile

    if not profile:
        st.info("👆 Commencez par analyser votre CV dans la page 'CV'.")
        uploaded = st.file_uploader("Ou uploader un CV ici", type=["pdf"])
        if uploaded:
            with st.spinner("Analyse..."):
                file_bytes = uploaded.read()
                result = analyze_cv_api(file_bytes, uploaded.name)
                if result:
                    profile = result.get("profile", {})
                    st.session_state.cv_profile = profile
                    st.success("✅ CV analysé !")
                else:
                    st.error("Erreur lors de l'analyse.")
                    return
    else:
        st.success(f"✅ Profil utilisé : {profile.get('name', 'Inconnu')} – {len(profile.get('skills', []))} compétences")

    if profile:
        with st.spinner("Recherche des offres recommandées..."):
            result = recommendations_api(profile, top_n=10)
            recs = result if isinstance(result, list) else []

            if recs and len(recs) > 0:
                st.subheader("🏢 Offres recommandées")
                for i, rec in enumerate(recs[:5], 1):
                    score = rec.get('score', 0)
                    badge_class = "badge-success" if score >= 70 else "badge-warning" if score >= 50 else "badge-danger"
                    expander_label = f"{i}. {rec.get('title', 'Offre')} – {rec.get('company', 'Inconnue')}  [{score}%]"

                    with st.expander(expander_label):
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.2rem; font-weight: 600;">{rec.get('title', 'Offre')}</span>
                            <span class="{badge_class}">{score}%</span>
                        </div>
                        <hr style="border-color: var(--border);">
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Entreprise :** {rec.get('company', 'Inconnue')}")
                            st.write(f"**Localisation :** {rec.get('location', 'Non spécifiée')}")
                            st.write(f"**Compétences communes ({rec.get('common_count', 0)}) :**")
                            st.write(", ".join(rec.get('common_skills', [])) if rec.get('common_skills') else "Aucune")
                        with col2:
                            st.write(f"**Compétences manquantes ({len(rec.get('missing_skills', []))}) :**")
                            st.write(", ".join(rec.get('missing_skills', [])) if rec.get('missing_skills') else "Aucune")
            else:
                st.info("Aucune recommandation trouvée.")

    st.markdown("---")
    st.subheader("📊 Analyser votre écart de compétences (Skill Gap)")
    job_text = st.text_area("Description du poste", height=100,
                            placeholder="Exemple : Data Scientist avec Python, SQL, AWS, Docker et Machine Learning.")

    if st.button("🔍 Calculer le skill gap", use_container_width=True) and job_text:
        if not profile:
            st.warning("Veuillez d'abord analyser un CV.")
        else:
            with st.spinner("Calcul du skill gap..."):
                gap_result = skill_gap_api(profile, job_text)
                if gap_result:
                    st.session_state.gap_result = gap_result
                    st.success("✅ Skill gap calculé !")
                else:
                    st.error("Erreur lors du calcul.")

    gap_result = st.session_state.gap_result
    if gap_result:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Compétences manquantes", gap_result.get("total_missing", 0))
        with col2:
            if gap_result.get("total_missing", 0) == 0:
                st.success("🎯 Votre profil correspond parfaitement !")
            else:
                st.warning(f"⚠️ Il vous manque {gap_result['total_missing']} compétences")

        if gap_result.get("gap_by_category"):
            st.subheader("📈 Détail par catégorie")
            for cat, skills in gap_result["gap_by_category"].items():
                st.write(f"**{cat} :** {', '.join(skills)}")

        if gap_result.get("missing_skills"):
            st.subheader("📚 Suggestions de carrière")
            suggestions = []
            for skill in gap_result["missing_skills"][:5]:
                suggestions.append({
                    'skill': skill,
                    'ressource': f"Formation en {skill} – Coursera / Udemy",
                    'estimation': "2-4 semaines"
                })

            cols = st.columns(min(len(suggestions), 3))
            for idx, sugg in enumerate(suggestions):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <strong style="font-size: 1.05rem;">{sugg['skill']}</strong><br>
                        <span style="color: var(--text-2);">{sugg['ressource']}</span><br>
                        <span style="font-size: 0.8rem; color: var(--text-3);">⏱️ {sugg['estimation']}</span>
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("📤 Exporter les suggestions", key="export_suggestions"):
                json_str = json.dumps(suggestions, indent=2, ensure_ascii=False)
                st.download_button("📥 Télécharger JSON", data=json_str,
                                   file_name="suggestions_carriere.json", mime="application/json")

def page_salaire():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown("<div class='main-header'>💰 Prédiction de salaire</div>", unsafe_allow_html=True)
    st.write("Renseignez les caractéristiques du poste pour estimer le salaire.")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Intitulé du poste", "Data Scientist")
        experience = st.selectbox("Niveau d'expérience", ["Entry-Level", "Mid-Level", "Senior", "Lead"])
        remote = st.selectbox("Remote autorisé", [0, 1], format_func=lambda x: "Oui" if x else "Non")
    with col2:
        work_type = st.selectbox("Type de contrat", ["Full-time", "Part-time", "Contract"])
        location = st.text_input("Localisation", "New York, NY")
        min_salary = st.number_input("Salaire minimum (USD)", min_value=0, value=70000)
        max_salary = st.number_input("Salaire maximum (USD)", min_value=0, value=110000)

    if st.button("🔮 Prédire le salaire"):
        features = {
            "title": title,
            "formatted_experience_level": experience,
            "remote_allowed": remote,
            "work_type": work_type,
            "location": location,
            "min_salary": min_salary,
            "max_salary": max_salary
        }
        with st.spinner("Calcul..."):
            result = salary_api(features)
            if result:
                pred = result.get('predicted_salary', 0)
                min_range = result.get('min_range', pred * 0.85)
                max_range = result.get('max_range', pred * 1.15)
                st.success("✅ Prédiction terminée")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💰 Salaire estimé", f"${pred:,.0f}")
                with col2:
                    st.metric("📉 Fourchette basse", f"${min_range:,.0f}")
                with col3:
                    st.metric("📈 Fourchette haute", f"${max_range:,.0f}")

                fig = go.Figure(go.Indicator(
                    mode="number+gauge",
                    value=pred,
                    title={"text": "Salaire estimé (USD)"},
                    domain={"x": [0,1], "y":[0,1]},
                    gauge={
                        "axis": {"range": [0, 200000]},
                        "bar": {"color": "#22c55e"},
                        "bgcolor": "rgba(0,0,0,0)",
                        "steps": [
                            {"range": [0, 50000], "color": "rgba(244,63,94,0.18)"},
                            {"range": [50000, 100000], "color": "rgba(245,165,36,0.18)"},
                            {"range": [100000, 200000], "color": "rgba(34,197,94,0.18)"}
                        ]
                    }
                ))
                st.plotly_chart(style_fig(fig), use_container_width=True)

def page_comparateur():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📊 Comparateur d\'offres</div>', unsafe_allow_html=True)
    st.write("Comparez deux offres d'emploi et leur adéquation avec votre profil.")

    profile = st.session_state.cv_profile
    if not profile:
        st.info("💡 Pour un matching personnalisé, analysez d'abord votre CV dans la page dédiée.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📌 Offre 1")
        title1 = st.text_input("Titre", key="title1", placeholder="Data Scientist")
        company1 = st.text_input("Entreprise", key="comp1", placeholder="Tech Corp")
        skills1 = st.text_area("Compétences (séparées par des virgules)", key="skills1",
                               placeholder="Python, SQL, Machine Learning")
        salary1 = st.number_input("Salaire (USD)", min_value=0, value=80000, step=5000, key="sal1")
        remote1 = st.selectbox("Remote", ["Oui", "Non"], key="remote1")
    with col2:
        st.subheader("📌 Offre 2")
        title2 = st.text_input("Titre", key="title2", placeholder="ML Engineer")
        company2 = st.text_input("Entreprise", key="comp2", placeholder="AI Startup")
        skills2 = st.text_area("Compétences (séparées par des virgules)", key="skills2",
                               placeholder="Python, TensorFlow, AWS")
        salary2 = st.number_input("Salaire (USD)", min_value=0, value=90000, step=5000, key="sal2")
        remote2 = st.selectbox("Remote", ["Oui", "Non"], key="remote2")

    if st.button("🔍 Comparer", use_container_width=True):
        if not (title1 and title2 and skills1 and skills2):
            st.warning("Veuillez remplir les titres et les compétences pour les deux offres.")
            return

        set1 = set([s.strip().lower() for s in skills1.split(',') if s.strip()])
        set2 = set([s.strip().lower() for s in skills2.split(',') if s.strip()])
        common = set1 & set2
        only1 = set1 - set2
        only2 = set2 - set1

        st.subheader("📋 Comparaison détaillée")
        data = [
            ["Critère", "Offre 1", "Offre 2"],
            ["Titre", title1, title2],
            ["Entreprise", company1, company2],
            ["Salaire", f"${salary1:,}", f"${salary2:,}"],
            ["Remote", remote1, remote2],
            ["Nb compétences", len(set1), len(set2)],
            ["Compétences communes", ", ".join(sorted(common)) if common else "Aucune", ""],
            ["Compétences uniques", ", ".join(sorted(only1)) if only1 else "Aucune", ", ".join(sorted(only2)) if only2 else "Aucune"]
        ]
        html_table = "<table class='comp-table'>"
        for row in data:
            html_table += "<tr>"
            for cell in row:
                html_table += f"<td>{cell}</td>"
            html_table += "</tr>"
        html_table += "</table>"
        st.markdown(html_table, unsafe_allow_html=True)

        comp_df = pd.DataFrame({
            "Offre": ["Offre 1", "Offre 2"],
            "Compétences": [len(set1), len(set2)],
            "Salaire (k$)": [salary1/1000, salary2/1000]
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(x=comp_df["Offre"], y=comp_df["Compétences"], name="Nb compétences", marker_color="#8b5cf6"))
        fig.add_trace(go.Bar(x=comp_df["Offre"], y=comp_df["Salaire (k$)"], name="Salaire (k$)", marker_color="#ec4899"))
        fig.update_layout(barmode='group', title="Comparaison des offres", yaxis_title="Valeurs")
        st.plotly_chart(style_fig(fig), use_container_width=True)

        if profile:
            st.subheader("🎯 Adéquation avec votre profil")
            cv_skills = set(profile.get('skills', []))
            cols = st.columns(2)
            for idx, (title, skill_set, salary) in enumerate([(title1, set1, salary1), (title2, set2, salary2)], start=1):
                common_cv = cv_skills & skill_set
                missing_cv = skill_set - cv_skills
                score = len(common_cv) / len(skill_set) * 100 if skill_set else 0
                with cols[idx-1]:
                    st.markdown(f"#### Offre {idx} : {title}")
                    st.metric("Score de matching", f"{score:.1f}%")
                    st.progress(score/100)
                    st.write(f"**Compétences communes :** {', '.join(sorted(common_cv)) if common_cv else 'Aucune'}")
                    st.write(f"**Compétences manquantes :** {', '.join(sorted(missing_cv)) if missing_cv else 'Aucune'}")
                    if score >= 80:
                        st.success("✅ Excellente adéquation !")
                    elif score >= 50:
                        st.warning("⚠️ Adéquation moyenne, quelques lacunes.")
                    else:
                        st.error("❌ Adéquation faible, beaucoup de compétences manquantes.")
        else:
            st.info("Analysez votre CV pour voir l'adéquation personnalisée.")

def page_analyse_carriere():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📊 Analyse de carrière</div>', unsafe_allow_html=True)
    profile = st.session_state.cv_profile
    if not profile:
        st.warning("⚠️ Veuillez d'abord analyser un CV dans la page 'CV'.")
        return

    st.write(f"Analyse pour : **{profile.get('name', 'Inconnu')}**")

    skills = profile.get('skills', [])
    nb_skills = len(skills)
    seniority = profile.get('seniority', 'junior')

    if seniority == 'junior':
        next_title = "Mid-Level"
        salary_growth = 20
    elif seniority == 'mid':
        next_title = "Senior"
        salary_growth = 15
    elif seniority == 'senior':
        next_title = "Lead / Manager"
        salary_growth = 10
    else:
        next_title = "Expert"
        salary_growth = 8

    if nb_skills < 5:
        recommandation_skills = ["Apprendre Python", "SQL", "Machine Learning"]
    elif nb_skills < 10:
        recommandation_skills = ["Deep Learning", "Cloud (AWS/Azure)", "Big Data"]
    else:
        recommandation_skills = ["Leadership", "Gestion de projet", "Architecture système"]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Évolution prévue")
        st.metric("Poste suivant", next_title)
        st.metric("Augmentation salariale estimée", f"+{salary_growth}%")
        st.write(f"**Délai estimé :** {2 if seniority=='junior' else 3 if seniority=='mid' else 4} ans")
    with col2:
        st.subheader("🎯 Compétences à acquérir")
        for skill in recommandation_skills:
            st.write(f"- {skill}")

    years = [2023, 2024, 2025, 2026, 2027]
    salaires = [70000, 75000, 82000, 90000, 105000]
    fig = px.line(x=years, y=salaires, title="Progression salariale estimée", labels={'x':'Année', 'y':'Salaire (USD)'},
                  color_discrete_sequence=["#8b5cf6"])
    st.plotly_chart(style_fig(fig), use_container_width=True)

def get_response(question, profile=None):
    payload = {
        "question": question,
        "profile": profile if profile else None,
        "history": [{"role": r, "content": m} for r, m in st.session_state.chat_history[-5:]]
    }
    result = api_call("POST", "/chatbot/", json=payload)
    if result and "response" in result:
        return result["response"]
    return "⚠️ Erreur du chatbot"

def page_assistant():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">🤖 Assistant carrière</div>', unsafe_allow_html=True)
    st.write("Posez vos questions sur les métiers, les compétences, les formations...")

    if not st.session_state.chat_history:
        welcome = "Bonjour ! Je suis votre assistant carrière. Posez-moi une question ou cliquez sur une suggestion ci-dessous."
        st.session_state.chat_history = [("assistant", welcome)]

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role if role == "user" else "assistant"):
            st.markdown(msg)

    st.markdown("### 💡 Suggestions")
    cols = st.columns(3)
    suggestions = [
        "Quelles compétences sont les plus demandées ?",
        "Comment améliorer mon CV ?",
        "Quel salaire pour un Data Scientist ?",
        "Quelles formations suivre ?",
        "Quels métiers dans la Data ?",
        "Conseils personnalisés pour moi"
    ]
    for i, sugg in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(sugg, key=f"sugg_{i}"):
                response = get_response(sugg, profile=st.session_state.cv_profile)
                st.session_state.chat_history.append(("user", sugg))
                st.session_state.chat_history.append(("assistant", response))
                st.rerun()

    user_input = st.chat_input("Votre question...")
    if user_input:
        response = get_response(user_input, profile=st.session_state.cv_profile)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", response))
        st.rerun()

def page_rapport():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown('<div class="main-header">📄 Rapport personnalisé</div>', unsafe_allow_html=True)
    st.write("Générez un rapport PDF professionnel récapitulatif de votre analyse.")

    profile = st.session_state.cv_profile
    if not profile:
        st.warning("⚠️ Veuillez d'abord analyser un CV dans la page 'CV'.")
        return

    recs = []
    salary_pred = None
    if profile:
        try:
            recs_result = recommendations_api(profile, top_n=3)
            if recs_result and isinstance(recs_result, list):
                recs = recs_result
        except:
            pass
        salary_pred = {"predicted_salary": 95000, "min_range": 85000, "max_range": 105000}

    score = compute_cv_score(profile)
    st.info(f"📊 Score du CV : **{score}/100**")

    if st.button("📥 Télécharger le rapport PDF", use_container_width=True):
        with st.spinner("Génération du PDF..."):
            pdf_data = generate_pdf_report(profile, score, recs, salary_pred)
            st.success("✅ Rapport PDF généré avec succès !")
            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf_data,
                file_name=f"rapport_jobpulseai_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )

# ============================================================
# ROUTAGE PRINCIPAL
# ============================================================
if "nav" in st.session_state:
    page = st.session_state.pop("nav")
    st.session_state.current_page = page

page = st.session_state.current_page

if page == "🏠 Accueil":
    page_accueil()
elif page == "📈 Marché":
    page_marche()
elif page == "📈 Tendances":
    page_tendances()
elif page == "📄 CV":
    page_cv()
elif page == "🤝 Matching":
    page_matching()
elif page == "🎯 Recommandations":
    page_recommandations()
elif page == "💰 Salaire":
    page_salaire()
elif page == "📊 Comparateur":
    page_comparateur()
elif page == "📊 Analyse carrière":
    page_analyse_carriere()
elif page == "🤖 Assistant":
    page_assistant()
elif page == "📄 Rapport":
    page_rapport()

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")

cols = st.columns([2, 1, 1.5])

with cols[0]:
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <span style="font-family:'Sora',sans-serif; font-size:1.5rem; font-weight:800;
             background: linear-gradient(135deg, #8b5cf6, #ec4899);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            JobPulseAI
        </span>
    </div>
    <p style="color:var(--text-3); font-size:0.9rem; line-height:1.6; max-width:300px;">
        AI-Powered Career Intelligence · Aide les talents à trouver leur voie et les entreprises à recruter plus intelligemment.
    </p>
    <div style="margin-top:0.5rem; font-size:0.8rem; color:var(--text-3);">
        MMXXVI · JobPulseAI Co. · Public Benefit Co.
    </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown("**Produit**")
    if st.button("Home", key="footer_home", use_container_width=True):
        st.session_state["nav"] = "🏠 Accueil"
        st.rerun()
    if st.button("Marché", key="footer_market", use_container_width=True):
        st.session_state["nav"] = "📈 Marché"
        st.rerun()
    if st.button("CV", key="footer_cv", use_container_width=True):
        st.session_state["nav"] = "📄 CV"
        st.rerun()
    if st.button("Matching", key="footer_matching", use_container_width=True):
        st.session_state["nav"] = "🤝 Matching"
        st.rerun()
    if st.button("Recommandations", key="footer_reco", use_container_width=True):
        st.session_state["nav"] = "🎯 Recommandations"
        st.rerun()

with cols[2]:
    st.markdown("**Recevoir les mises à jour**")
    st.caption("Recevez les dernières analyses et offres recommandées.")
    email = st.text_input("Email", placeholder="Votre e-mail", key="footer_email", label_visibility="collapsed")
    if st.button("Je m'abonne", key="footer_subscribe", use_container_width=True):
        if email:
            st.success(f"✅ Merci {email} ! Vous recevrez nos mises à jour.")
        else:
            st.warning("Veuillez entrer une adresse email.")
    st.caption("En vous inscrivant, vous acceptez notre politique de confidentialité.")

st.markdown("---")
col_left, col_right = st.columns([2, 1])
with col_left:
    st.caption("© 2026 JobPulseAI · Politique de confidentialité · Conditions d'utilisation")
with col_right:
    st.markdown("""
    <div style="display:flex; gap:0.8rem; justify-content:flex-end; font-size:1.1rem;">
        <a href="#" style="color:var(--text-3); text-decoration:none;">🔗</a>
        <a href="#" style="color:var(--text-3); text-decoration:none;">🐦</a>
        <a href="#" style="color:var(--text-3); text-decoration:none;">💼</a>
        <a href="#" style="color:var(--text-3); text-decoration:none;">📺</a>
    </div>
    """, unsafe_allow_html=True)
