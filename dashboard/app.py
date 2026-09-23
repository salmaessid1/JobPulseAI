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
import re as _re
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
    "accent_theme": "violet",
    "language": "FR",
    "search_query": "",
    "notifications_count": 0,
    "recent_actions": [],
        "conversations": {},          
    "current_conv_id": None,      # ID de la conversation active
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# SYSTÈME DE TRADUCTION (i18n)
# ============================================================
TRANSLATIONS = {
    "FR": {
        "search": "Recherche",
        "search_placeholder": "Offres, compétences...",
        "api_online": "API connectée",
        "api_offline": "API hors ligne",
        "menu": "Menu",
        "quick_actions": "Actions rapides",
        "recent": "Activité récente",
        "preferences": "Préférences",
        "dark_mode": "Mode sombre",
        "auto_refresh": "Auto-refresh (15s)",
        "language": "Langue",
        "accent_color": "Couleur d'accent",
        "overview": "En un coup d'œil",
        "offers": "Offres",
        "skills": "Compétences",
        "companies": "Entreprises",
        "remote_rate": "Taux remote",
        "session": "Session",
        "reset_cv": "Reset CV",
        "cache": "Cache",
        "refresh": "Actualiser",
        "help": "Aide & Support",
        "notifications": "Notifications",
        "no_notifications": "Aucune notification",
        "mark_read": "Marquer comme lues",
        "new_offers": "nouvelle(s) offre(s)",
        "matching_profile": "Correspondent à votre profil",
        "no_cv": "Aucun CV chargé",
        "load_cv": "Chargez votre CV pour commencer",
        "profile_complete": "Profil complété",
        "activity_7d": "Activité (7 derniers jours)",
        "data_unavailable": "Données indisponibles",
        "page_home": "🏠 Accueil",
        "page_market": "📈 Marché",
        "page_cv": "📄 CV",
        "page_matching": "🤝 Matching",
        "page_recommendations": "🎯 Recommandations",
        "page_salary": "💰 Salaire",
        "page_comparator": "📊 Comparateur",
        "page_career": "📊 Analyse carrière",
        "page_assistant": "🤖 Assistant",
        "page_report": "📄 Rapport",
        "section_indicators": "📌 Indicateurs clés",
        "section_performance": "🎯 Performance du recrutement & matching",
        "section_market": "📊 Analyse du marché de l'emploi",
        "dashboard_title": "📊 Tableau de bord – Performance du recrutement",
        "dashboard_subtitle": "Comprenez la performance de votre recrutement en temps réel.",
        "last_update": "Dernière mise à jour",
        "product": "Produit",
        "updates": "Recevoir les mises à jour",
        "subscribe": "Je m'abonne",
        "email_placeholder": "Votre e-mail",
        "privacy": "En vous inscrivant, vous acceptez notre politique de confidentialité.",
        "all_rights": "© 2026 JobPulseAI · Politique de confidentialité · Conditions d'utilisation",
        "market_title": "📈 Analyse du marché",
        "cv_title": "📄 Analyse de CV",
        "matching_title": "🤝 Matching CV / Offre",
        "reco_title": "🎯 Recommandations d'offres",
        "salary_title": "💰 Prédiction de salaire",
        "comparator_title": "📊 Comparateur d'offres",
        "career_title": "📊 Analyse de carrière",
        "assistant_title": "🤖 Assistant carrière",
        "report_title": "📄 Rapport personnalisé",
        "indicators": "📌 Indicateurs clés",
"active_offers": "Offres actives",
"matching_time": "Temps de matching moyen",
"reco_rate": "Taux de recommandation",
"ai_prediction": "Prédiction IA (acceptation)",
"performance_section": "🎯 Performance du recrutement & matching",
"matching_precision": "🎯 Précision du matching IA",
"hires_by_dept": "🏢 Recrutements par département",
"correspondence_dist": "📈 Distribution des correspondances",
"conversion": "🔄 Conversion des candidats",
"market_section": "📊 Analyse du marché de l'emploi",
"sectors_dist": "🏢 Répartition des offres par secteur",
"salaries_by_sector": "💰 Salaire moyen par secteur",
"top_cities": "🌍 Top 15 villes qui recrutent",
"remote_by_city": "🏠 Taux de remote par ville",
"cooccurrence": "🔥 Matrice de co-occurrence des compétences",
"data_unavailable": "Données indisponibles",
    },
    "EN": {
        "search": "Search",
        "search_placeholder": "Jobs, skills...",
        "api_online": "API connected",
        "api_offline": "API offline",
        "menu": "Menu",
        "quick_actions": "Quick actions",
        "recent": "Recent activity",
        "preferences": "Preferences",
        "dark_mode": "Dark mode",
        "auto_refresh": "Auto-refresh (15s)",
        "language": "Language",
        "accent_color": "Accent color",
        "overview": "Overview",
        "offers": "Jobs",
        "skills": "Skills",
        "companies": "Companies",
        "remote_rate": "Remote rate",
        "session": "Session",
        "reset_cv": "Reset CV",
        "cache": "Cache",
        "refresh": "Refresh",
        "help": "Help & Support",
        "notifications": "Notifications",
        "no_notifications": "No notifications",
        "mark_read": "Mark as read",
        "new_offers": "new offer(s)",
        "matching_profile": "Match your profile",
        "no_cv": "No CV loaded",
        "load_cv": "Upload your CV to start",
        "profile_complete": "Profile completion",
        "activity_7d": "Activity (last 7 days)",
        "data_unavailable": "Data unavailable",
        "page_home": "🏠 Home",
        "page_market": "📈 Market",
        "page_cv": "📄 Resume",
        "page_matching": "🤝 Matching",
        "page_recommendations": "🎯 Recommendations",
        "page_salary": "💰 Salary",
        "page_comparator": "📊 Comparator",
        "page_career": "📊 Career analysis",
        "page_assistant": "🤖 Assistant",
        "page_report": "📄 Report",
        "section_indicators": "📌 Key indicators",
        "section_performance": "🎯 Recruitment performance & matching",
        "section_market": "📊 Job market analysis",
        "dashboard_title": "📊 Dashboard – Recruitment performance",
        "dashboard_subtitle": "Understand your recruitment performance in real time.",
        "last_update": "Last update",
        "product": "Product",
        "updates": "Get updates",
        "subscribe": "Subscribe",
        "email_placeholder": "Your email",
        "privacy": "By subscribing, you agree to our privacy policy.",
        "all_rights": "© 2026 JobPulseAI · Privacy Policy · Terms of Use",
        "market_title": "📈 Market analysis",
        "cv_title": "📄 Resume analysis",
        "matching_title": "🤝 CV / Job matching",
        "reco_title": "🎯 Job recommendations",
        "salary_title": "💰 Salary prediction",
        "comparator_title": "📊 Job comparator",
        "career_title": "📊 Career analysis",
        "assistant_title": "🤖 Career assistant",
        "report_title": "📄 Personalized report",
        "indicators": "📌 Key indicators",
"active_offers": "Active jobs",
"matching_time": "Average matching time",
"reco_rate": "Recommendation rate",
"ai_prediction": "AI prediction (acceptance)",
"performance_section": "🎯 Recruitment performance & matching",
"matching_precision": "🎯 AI matching precision",
"hires_by_dept": "🏢 Hires by department",
"correspondence_dist": "📈 Correspondence distribution",
"conversion": "🔄 Candidate conversion",
"market_section": "📊 Job market analysis",
"sectors_dist": "🏢 Jobs by sector",
"salaries_by_sector": "💰 Average salary by sector",
"top_cities": "🌍 Top 15 hiring cities",
"remote_by_city": "🏠 Remote rate by city",
"cooccurrence": "🔥 Skill co-occurrence matrix",
"data_unavailable": "Data unavailable",
    },
}


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
# ============================================================
# THÈME ACCENT DYNAMIQUE
# ============================================================
ACCENT_THEMES = {
    "violet":   {"primary": "#8b5cf6", "secondary": "#ec4899"},
    "bleu":     {"primary": "#3b82f6", "secondary": "#06b6d4"},
    "rose":     {"primary": "#ec4899", "secondary": "#f43f5e"},
    "emeraude": {"primary": "#10b981", "secondary": "#22c55e"},
}
def tr(key: str) -> str:
    lang = st.session_state.get("language", "FR")
    return TRANSLATIONS.get(lang, TRANSLATIONS["FR"]).get(key, key)
# ============================================================
# CSS PERSONNALISÉ (MediCore 2026)
# ============================================================
def apply_css(dark=True):
    if dark:
        tokens = {
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

        * {{ scrollbar-width: thin; scrollbar-color: var(--border-strong) transparent; }}
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

        section[data-testid="stSidebar"] {{
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border);
            overflow-x: hidden !important;
            overflow-y: auto !important;
            height: 100vh !important;
        }}
        section[data-testid="stSidebar"] > div {{ overflow: visible !important; height: auto !important; }}
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
            overflow: visible !important;
            padding: 0.8rem 0.85rem 1.5rem 0.85rem !important;
        }}
        section[data-testid="stSidebar"] * {{ color: var(--text-1); box-sizing: border-box; }}
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stCaption {{ color: var(--text-2); }}

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
            gap: 0.25rem !important;
        }}
        section[data-testid="stSidebar"] .element-container {{ margin-bottom: 0.1rem !important; }}
        section[data-testid="stSidebar"] hr {{ margin: 0.5rem 0 !important; }}
        section[data-testid="stSidebar"] .stButton > button {{
            padding: 0.35rem 0.8rem !important;
            font-size: 0.78rem !important;
            min-height: 32px !important;
        }}
        section[data-testid="stSidebar"] .stTextInput > div > div > input {{
            padding: 0.35rem 0.6rem !important;
            font-size: 0.82rem !important;
            min-height: 32px !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox > div > div {{
            min-height: 32px !important;
            font-size: 0.82rem !important;
        }}
        section[data-testid="stSidebar"] label {{ font-size: 0.78rem !important; }}
        section[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: 2px !important; display: flex; flex-direction: column; }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            background: transparent;
            border-radius: var(--radius-sm);
            padding: 6px 10px !important;
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
            box-shadow: 0 4px 12px rgba(139,92,246,0.3);
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p,
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {{
            color: #ffffff !important;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {{
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            margin: 0 !important;
        }}

        .sidebar-section-label {{
            font-size: 0.62rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-3) !important;
            margin: 0.5rem 0 0.25rem 0.1rem !important;
            display: block;
        }}

        .sidebar-divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border) 15%, var(--border) 85%, transparent);
            margin: 0.5rem 0 !important;
        }}

        .sidebar-metrics {{
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 0.5rem 0.7rem !important;
            margin: 0.2rem 0 0.3rem 0;
        }}
        .sidebar-metrics .metric {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.2rem 0 !important;
            border-bottom: 1px dashed var(--border);
        }}
        .sidebar-metrics .metric:last-child {{ border-bottom: none; }}
        .sidebar-metrics .label {{ color: var(--text-2); font-size: 0.75rem !important; }}
        .sidebar-metrics .value {{ font-weight: 700; color: var(--text-1); font-size: 0.78rem !important; }}

        .sidebar-footer {{
            margin-top: 0.6rem !important;
            padding-top: 0.5rem !important;
            border-top: 1px solid var(--border);
            color: var(--text-3);
            display: flex;
            flex-direction: column;
            gap: 0.1rem !important;
        }}

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

        .stButton > button {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
            color: white; border: none;
            border-radius: var(--radius-sm);
            padding: 0.64rem 1.6rem;
            font-weight: 700;
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

        div[data-testid="stContainer"] {{
            background: var(--surface-solid);
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            padding: 1rem !important;
        }}
            /* ============================================================
           CHATBOT PREMIUM
           ============================================================ */
        .stChatMessage {{
            background: var(--surface-solid) !important;
            border: 1px solid var(--border) !important;
            border-radius: 16px !important;
            padding: 1rem 1.2rem !important;
            margin-bottom: 0.5rem !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            animation: fadeIn 0.3s ease;
        }}

        .stChatInputContainer {{
            border-radius: 12px !important;
            border: 1px solid var(--border-strong) !important;
            background: var(--surface-solid) !important;
        }}

        .stChatInputContainer:focus-within {{
            border-color: var(--accent-1) !important;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: var(--surface-2);
            padding: 4px;
            border-radius: 12px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px !important;
            padding: 6px 12px !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--accent-1), var(--accent-2)) !important;
            color: white !important;
        }}

        /* Boutons suggestion */
        .stButton > button[kind="secondary"] {{
            background: var(--surface-2) !important;
            color: var(--text-1) !important;
            border: 1px solid var(--border) !important;
            font-size: 0.78rem !important;
            padding: 0.5rem 0.8rem !important;
            text-align: left !important;
            transition: all 0.2s !important;
        }}

        .stButton > button[kind="secondary"]:hover {{
            background: var(--surface-solid) !important;
            border-color: var(--accent-1) !important;
            transform: translateX(4px);
        }}
    </style>
        
    """, unsafe_allow_html=True)
    
apply_css(st.session_state.dark_mode)

# ============================================================
# APPLICATION DU THÈME ACCENT DYNAMIQUE
# ============================================================
theme = ACCENT_THEMES.get(st.session_state.accent_theme, ACCENT_THEMES["violet"])
st.markdown(f"""
<style>
    :root {{
        --accent-1: {theme['primary']} !important;
        --accent-2: {theme['secondary']} !important;
    }}
</style>

""", unsafe_allow_html=True)

# ============================================================
# FONCTIONS API (inchangées)
# ============================================================

def _fetch_silent(endpoint, timeout=30):
    """Appelle l'API via requests (compatible Windows ET Linux/Streamlit Cloud)."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        print(f"🔵 GET {url}")
        # proxies=None désactive tout proxy système (comme le fait curl)
        resp = requests.get(
            url,
            timeout=timeout,
            proxies={"http": None, "https": None},
            headers={"User-Agent": "JobPulseAI/5.2"},
        )
        print(f"✅ {resp.status_code} - {endpoint}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout sur {endpoint} après {timeout}s")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"🔴 Connexion échouée sur {endpoint} : {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"🔴 HTTP {e.response.status_code} sur {endpoint}")
        return None
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



    
@st.cache_data(ttl=120, show_spinner=False)# rafraîchissement toutes les 15 secondes maximum.
def get_realtime_snapshot():
    """Récupère un snapshot temps réel (stats + notifications + activité)."""
    return _fetch_silent("/stats/realtime/snapshot")




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
    if len(skills) >= 10: score += 30
    elif len(skills) >= 5: score += 20
    elif len(skills) >= 3: score += 10
    domains = profile.get('domains', [])
    if len(domains) >= 3: score += 20
    elif len(domains) >= 1: score += 10
    seniority = profile.get('seniority', '')
    if seniority in ['senior', 'lead']: score += 20
    elif seniority == 'mid': score += 10
    else: score += 5
    return min(score, 100)

PLOTLY_TEMPLATE = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
CHART_COLORWAY = ["#8b5cf6", "#ec4899", "#3b82f6", "#f5a524", "#f43f5e", "#22c55e"]
def chatbot_api(question, profile=None, history=None):
    return api_call("POST", "/chatbot/", json={
        "question": question,
        "profile": profile,
        "history": history or []
    })
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
# ============================================================
# SIDEBAR AMÉLIORÉE (v6.0)
# ============================================================



with st.sidebar:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div { gap: 0.25rem !important; }
        section[data-testid="stSidebar"] .element-container { margin-bottom: 0.1rem !important; }
        section[data-testid="stSidebar"] hr { margin: 0.5rem 0 !important; }
        section[data-testid="stSidebar"] .stButton > button {
            padding: 0.35rem 0.8rem !important; font-size: 0.78rem !important; min-height: 32px !important;
        }
        section[data-testid="stSidebar"] .stTextInput > div > div > input {
            padding: 0.35rem 0.6rem !important; font-size: 0.82rem !important; min-height: 32px !important;
        }
        section[data-testid="stSidebar"] .stSelectbox > div > div { min-height: 32px !important; font-size: 0.82rem !important; }
        section[data-testid="stSidebar"] label { font-size: 0.78rem !important; }
        section[data-testid="stSidebar"] .sidebar-section-label {
            margin: 0.5rem 0 0.25rem 0.1rem !important; font-size: 0.62rem !important;
        }
        section[data-testid="stSidebar"] .sidebar-divider { margin: 0.5rem 0 !important; }
        section[data-testid="stSidebar"] .sidebar-metrics { padding: 0.5rem 0.7rem !important; }
        section[data-testid="stSidebar"] .sidebar-metrics .metric { padding: 0.2rem 0 !important; }
        section[data-testid="stSidebar"] .sidebar-metrics .label,
        section[data-testid="stSidebar"] .sidebar-metrics .value { font-size: 0.75rem !important; }
        section[data-testid="stSidebar"] .sidebar-footer {
            margin-top: 0.6rem !important; padding-top: 0.5rem !important; gap: 0.1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.3rem;">
        <div style="width:34px; height:34px; border-radius:9px; flex-shrink:0;
             background:linear-gradient(135deg,#8b5cf6,#ec4899);
             display:flex; align-items:center; justify-content:center;
             font-size:1rem; box-shadow:0 4px 12px rgba(139,92,246,0.3);">📊</div>
        <div style="line-height:1.1;">
            <div style="font-family:'Sora',sans-serif; font-weight:800; font-size:1rem;
                 background:linear-gradient(135deg,#8b5cf6,#ec4899);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;">JobPulseAI</div>
            <div style="color:var(--text-3); font-size:0.6rem; letter-spacing:0.05em; font-weight:600;">
                v6.1 · {lang}
            </div>
        </div>
    </div>
    """.format(lang=st.session_state.language), unsafe_allow_html=True)

    # ========== 2. BARRE DE RECHERCHE GLOBALE ==========
    search_input = st.text_input(
        "🔍 Recherche",
        placeholder="Offres, compétences, entreprises...",
        key="search_bar",
        label_visibility="collapsed",
    )
    if search_input:
        st.session_state.search_query = search_input
        # Feedback visuel
        st.markdown(f"""
        <div style="background:var(--surface-2); border-radius:8px; padding:0.5rem 0.7rem; margin-top:0.3rem;">
            <div style="font-size:0.7rem; color:var(--text-3);">Recherche en cours pour :</div>
            <div style="font-weight:600; font-size:0.85rem;">"{search_input}"</div>
            <div style="font-size:0.7rem; color:var(--accent-1); margin-top:0.2rem;">Utilisez la page Marché pour voir les résultats</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ========== 3. STATUT API AVEC LATENCE ==========
    # ========== 3. STATUT API TEMPS RÉEL ==========
    snapshot = get_realtime_snapshot()
    stats = snapshot if snapshot else get_global_stats()
    
    api_ok = stats is not None
    status_color = "#22c55e" if api_ok else "#f43f5e"
    status_label = tr("api_online") if api_ok else tr("api_offline")
    
    last_update = datetime.now().strftime("%H:%M:%S")
    
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; 
         background:var(--surface-2); border-radius:8px; padding:0.35rem 0.6rem; margin:0.3rem 0;">
        <div style="display:flex; align-items:center; gap:0.4rem;">
            <span style="width:7px; height:7px; border-radius:50%; background:{status_color};
                 box-shadow:0 0 0 2px {status_color}26; animation:pulse 2s infinite;"></span>
            <span style="font-size:0.7rem; color:var(--text-2); font-weight:600;">{status_label}</span>
        </div>
        <span style="font-size:0.62rem; color:var(--text-3); font-weight:600;">🕒 {last_update}</span>
    </div>
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ========== 4. PROFIL UTILISATEUR (inchangé) ==========
    profile = st.session_state.cv_profile
    if profile:
        name = profile.get('name', 'User')
        initials = ''.join([w[0].upper() for w in name.split()[:2]]) if name else "?"
        skills_count = len(profile.get('skills', []))
        progress = min(100, (skills_count * 5) + (len(profile.get('domains', [])) * 10) + 20)

        st.markdown(f"""
        <div style="background:var(--surface); border:1px solid var(--border); border-radius:10px;
                    padding:0.55rem 0.65rem; margin:0.2rem 0 0.3rem 0;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <div style="width:30px; height:30px; border-radius:50%;
                     background:linear-gradient(135deg,#8b5cf6,#ec4899);
                     display:flex; align-items:center; justify-content:center;
                     font-weight:700; color:white; font-size:0.75rem; flex-shrink:0;">{initials}</div>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:700; font-size:0.78rem; overflow:hidden; 
                         text-overflow:ellipsis; white-space:nowrap;">{name}</div>
                    <div style="font-size:0.65rem; color:var(--text-3);">{skills_count} {tr("skills").lower()}</div>
                </div>
            </div>
            <div style="margin-top:0.4rem;">
                <div style="display:flex; justify-content:space-between; font-size:0.62rem; 
                     color:var(--text-3); margin-bottom:0.15rem;">
                    <span>{tr("profile_complete")}</span>
                    <span style="font-weight:700; color:var(--accent-1);">{progress}%</span>
                </div>
                <div style="height:4px; background:var(--surface-2); border-radius:2px; overflow:hidden;">
                    <div style="height:100%; width:{progress}%; 
                         background:linear-gradient(90deg,#8b5cf6,#ec4899); border-radius:2px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:var(--surface); border:1px dashed var(--border); border-radius:10px;
                    padding:0.5rem; text-align:center; margin:0.2rem 0 0.3rem 0;">
            <div style="font-size:1.1rem; margin-bottom:0.1rem;">👤</div>
            <div style="font-size:0.7rem; color:var(--text-2); font-weight:600;">{tr("no_cv")}</div>
            <div style="font-size:0.62rem; color:var(--text-3);">{tr("load_cv")}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ========== 5. NOTIFICATIONS TEMPS RÉEL ==========
    # ========== 5. NOTIFICATIONS TEMPS RÉEL ==========
    realtime_notif = snapshot.get("notifications", 0) if snapshot else 0

    if "last_seen_notif" not in st.session_state:
        st.session_state.last_seen_notif = 0

    has_new = realtime_notif > st.session_state.last_seen_notif

    col_n1, col_n2 = st.columns([3, 1])
    with col_n1:
        st.markdown(f'<p class="sidebar-section-label" style="margin:0;">🔔 {tr("notifications")}</p>', unsafe_allow_html=True)
    with col_n2:
        if realtime_notif > 0:
            pulse_css = "animation:pulse 1.5s infinite;" if has_new else ""
            st.markdown(f"""
            <div style="background:#ec4899; color:white; border-radius:999px; text-align:center;
                 font-size:0.6rem; font-weight:700; padding:0.1rem 0.4rem; {pulse_css}">{realtime_notif}</div>
            """, unsafe_allow_html=True)

    if realtime_notif > 0:
        latest = snapshot.get("latest_title", "") if snapshot else ""
        # Nettoyer tout HTML résiduel dans le titre
        latest = _re.sub(r'<[^>]+>', '', str(latest))
        latest = latest.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        latest = _re.sub(r'\s+', ' ', latest).strip()
        latest_short = latest[:50] + "..." if len(latest) > 50 else latest
        if not latest_short:
            latest_short = "Nouvelles offres disponibles"

        st.markdown(f"""
        <div style="background:var(--surface-2); border-radius:8px; padding:0.4rem 0.55rem; margin:0.2rem 0; border-left:3px solid #ec4899;">
            <div style="font-size:0.7rem; font-weight:600;">📢 {realtime_notif} {tr("new_offers")}</div>
            <div style="font-size:0.62rem; color:var(--text-3); margin-top:0.15rem;">{latest_short}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"✅ {tr('mark_read')}", key="clear_notifs", use_container_width=True):
            st.session_state.last_seen_notif = realtime_notif
            st.rerun()
    else:
        st.caption(tr("no_notifications"))

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    # ========== 6. MENU ==========
    st.markdown(f'<p class="sidebar-section-label">📋 {tr("menu")}</p>', unsafe_allow_html=True)
    page_labels = [tr("page_home"), tr("page_market"), tr("page_cv"),
                   tr("page_matching"), tr("page_recommendations"), tr("page_salary"),
                   tr("page_comparator"), tr("page_career"), tr("page_assistant"), tr("page_report")]
    pages_internal = ["🏠 Accueil", "📈 Marché", "📄 CV",
                      "🤝 Matching", "🎯 Recommandations", "💰 Salaire",
                      "📊 Comparateur", "📊 Analyse carrière", "🤖 Assistant", "📄 Rapport"]
    current_idx = pages_internal.index(st.session_state.current_page) if st.session_state.current_page in pages_internal else 0
    selected_label = st.radio("Navigation", page_labels, index=current_idx,
                              label_visibility="collapsed", key="nav_radio")
    if selected_label in page_labels:
        st.session_state.current_page = pages_internal[page_labels.index(selected_label)]

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ========== 7. ACTIONS RAPIDES ==========
    st.markdown(f'<p class="sidebar-section-label">⚡ {tr("quick_actions")}</p>', unsafe_allow_html=True)
    qa_col1, qa_col2 = st.columns(2)
    with qa_col1:
        if st.button("📄 CV", key="qa_cv", use_container_width=True):
            st.session_state["nav"] = "📄 CV"
            st.session_state.recent_actions.append(("📄 CV", datetime.now().strftime("%H:%M")))
            st.rerun()
    with qa_col2:
        if st.button("🤝 Match", key="qa_match", use_container_width=True):
            st.session_state["nav"] = "🤝 Matching"
            st.session_state.recent_actions.append(("🤝 Matching", datetime.now().strftime("%H:%M")))
            st.rerun()
    qa_col3, qa_col4 = st.columns(2)
    with qa_col3:
        if st.button("💰 Salary", key="qa_salary", use_container_width=True):
            st.session_state["nav"] = "💰 Salaire"
            st.session_state.recent_actions.append(("💰 Salaire", datetime.now().strftime("%H:%M")))
            st.rerun()
    with qa_col4:
        if st.button("📄 Report", key="qa_report", use_container_width=True):
            st.session_state["nav"] = "📄 Rapport"
            st.session_state.recent_actions.append(("📄 Rapport", datetime.now().strftime("%H:%M")))
            st.rerun()

    # ========== 8. HISTORIQUE RÉCENT ==========
    if st.session_state.recent_actions:
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="sidebar-section-label">📜 {tr("recent")}</p>', unsafe_allow_html=True)
        for action, ts in st.session_state.recent_actions[-2:][::-1]:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                 padding:0.25rem 0.5rem; background:var(--surface-2); border-radius:5px;
                 margin-bottom:0.15rem; font-size:0.7rem;">
                <span style="font-weight:600;">{action}</span>
                <span style="color:var(--text-3); font-size:0.62rem;">{ts}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ========== 9. PRÉFÉRENCES ==========
    st.markdown(f'<p class="sidebar-section-label">⚙️ {tr("preferences")}</p>', unsafe_allow_html=True)
    dark_mode = st.toggle(f"🌙 {tr('dark_mode')}", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()

    auto_refresh = st.toggle(f"🔄 {tr('auto_refresh')}", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    
    if auto_refresh:
        st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 15000);
        </script>
        """, unsafe_allow_html=True)
        st.caption(f"🟢 {tr('auto_refresh')} · 15s")


    def _on_lang_change():
        """Callback exécuté AVANT le rerun, met à jour la langue."""
        val = st.session_state.get("lang_select", "🇫🇷 Français")
        st.session_state.language = "FR" if "FR" in val else "EN"

    lang_options = ["🇫🇷 Français", "🇬🇧 English"]
    current_lang_idx = 0 if st.session_state.language == "FR" else 1
    st.selectbox(
        f"🌐 {tr('language')}",
        options=lang_options,
        index=current_lang_idx,
        key="lang_select",
        on_change=_on_lang_change,
    )

    accent_options = {"violet": "🟣 Violet", "bleu": "🔵 Bleu", "rose": "🩷 Rose", "emeraude": "🟢 Émeraude"}
    accent_keys = list(accent_options.keys())
    current_accent_idx = accent_keys.index(st.session_state.accent_theme) if st.session_state.accent_theme in accent_keys else 0
    selected_accent = st.selectbox(f"🎨 {tr('accent_color')}", options=list(accent_options.values()),
                                    index=current_accent_idx, key="accent_select")
    for key, label in accent_options.items():
        if label == selected_accent and key != st.session_state.accent_theme:
            st.session_state.accent_theme = key
            st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ========== 10. EN UN COUP D'ŒIL ==========
    # ========== 10. EN UN COUP D'ŒIL + MINI-GRAPHIQUE TEMPS RÉEL ==========
    st.markdown(f'<p class="sidebar-section-label">📊 {tr("overview")}</p>', unsafe_allow_html=True)
    if stats:
        st.markdown(f"""
        <div class="sidebar-metrics">
            <div class="metric"><span class="label">📋 {tr("offers")}</span><span class="value">{stats.get('total_jobs', 0):,}</span></div>
            <div class="metric"><span class="label">🧠 {tr("skills")}</span><span class="value">{stats.get('unique_skills', 0):,}</span></div>
            <div class="metric"><span class="label">🏢 {tr("companies")}</span><span class="value">{stats.get('unique_companies', 0):,}</span></div>
            <div class="metric"><span class="label">🌍 {tr("remote_rate")}</span><span class="value">{stats.get('remote_percent', 0):.1f}%</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mini-graphique temps réel
        activity = snapshot.get("activity", [0]*7) if snapshot else [0]*7
        labels = snapshot.get("activity_labels", [""]*7) if snapshot else [""]*7
        
        if any(activity):
            fig_spark = go.Figure()
            fig_spark.add_trace(go.Scatter(
                x=labels,
                y=activity,
                mode='lines+markers',
                line=dict(color='#8b5cf6', width=2),
                marker=dict(size=4, color='#ec4899'),
                fill='tozeroy',
                fillcolor='rgba(139,92,246,0.15)',
                hovertemplate='%{x}<br>%{y} offres<extra></extra>',
            ))
            fig_spark.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=5, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis=dict(visible=True, tickfont=dict(size=8, color='#65658a'), showgrid=False),
                yaxis=dict(visible=False),
                hoverlabel=dict(bgcolor="#1e293b", font_size=10),
            )
            st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})
            st.caption(f"📈 {tr('activity_7d')}")
        else:
            st.caption(f"⚠️ {tr('data_unavailable')}")
    else:
        st.caption(f"⚠️ {tr('data_unavailable')}")
    
    # ========== 11. SESSION & RESET ==========
    st.markdown(f'<p class="sidebar-section-label">🔧 {tr("session")}</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(f"🗑️ {tr('reset_cv')}", use_container_width=True, key="reset_cv"):
            st.session_state.cv_profile = None
            st.session_state.gap_result = None
            st.session_state.match_result = None
            st.success("OK")
            st.rerun()
    with col_b:
        if st.button(f"🧹 {tr('cache')}", use_container_width=True, key="clear_cache"):
            st.cache_data.clear()
            st.success("OK")
            st.rerun()
    if st.button(f"🔄 {tr('refresh')}", key="refresh_sidebar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # AIDE
    st.markdown(f'<p class="sidebar-section-label">❓ {tr("help")}</p>', unsafe_allow_html=True)
    help_col1, help_col2 = st.columns(2)
    with help_col1:
        st.markdown("""
        <a href="https://jobpulseai-ux5q.onrender.com/docs" target="_blank" 
           style="display:block; padding:0.35rem; background:var(--surface-2); 
           border-radius:6px; text-align:center; text-decoration:none; 
           color:var(--text-1); font-size:0.68rem; font-weight:600;">📚 API</a>
        """, unsafe_allow_html=True)
    with help_col2:
        st.markdown("""
        <a href="https://github.com" target="_blank"
           style="display:block; padding:0.35rem; background:var(--surface-2); 
           border-radius:6px; text-align:center; text-decoration:none; 
           color:var(--text-1); font-size:0.68rem; font-weight:600;">🐙 GitHub</a>
        """, unsafe_allow_html=True)

    # ========== 13. FOOTER ==========
    st.markdown(f"""
    <div class="sidebar-footer">
        <div style="font-size:0.62rem;">🔗 {API_BASE_URL.replace('https://', '').replace('http://', '')}</div>
        <div style="font-size:0.62rem;">🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
        <div style="font-size:0.62rem;">v{APP_VERSION} · {st.session_state.language}</div>
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
    st.caption(f"📅 {tr('last_update')} : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown(f'<div class="main-header">{tr("dashboard_title")}</div>', unsafe_allow_html=True)
    st.caption(tr("dashboard_subtitle"))

    if st.session_state.get("auto_refresh", False) and random.random() < 0.3:
        st.toast("📢 Une nouvelle offre correspond à votre profil !", icon="🎯")

    stats = get_global_stats()
    if not stats:
        st.warning(tr("data_unavailable"))
        return

    # Utiliser les données temps réel
    snapshot = get_realtime_snapshot()
    realtime_stats = snapshot if snapshot else stats
    
    # Variation basée sur l'activité réelle (différence entre les 2 derniers jours)
    activity = realtime_stats.get("activity", [0, 0])
    if len(activity) >= 2 and activity[-2] > 0:
        variation = int(((activity[-1] - activity[-2]) / activity[-2]) * 100)
    else:
        variation = 0
    
    total_jobs = realtime_stats.get('total_jobs', 0)
    st.markdown(f"### {tr('indicators')}")
    col1, col2, col3, col4 = st.columns(4)
    kpi_card(col1, "📊", tr("active_offers"), f"{total_jobs:,}", f"{variation:+d}%", "up", "#8b5cf6")
    kpi_card(col2, "⏳", tr("matching_time"), "7.3 j", "2%", "down", "#3b82f6")
    kpi_card(col3, "✅", tr("reco_rate"), "92%", None, "up", "#22c55e")
    kpi_card(col4, "🤖", tr("ai_prediction"), "86%", "4%", "up", "#ec4899")

    st.markdown("---")
    st.markdown(f"### {tr('performance_section')}")

    col_left, col_right = st.columns([1, 1])
    with col_left:
        with st.container(border=True):
            st.markdown(f"#### {tr('matching_precision')}")
            depts = ["Design", "Marketing", "Engineering", "Sales"]
            accuracy = [92.67, 78.5, 85.3, 72.1]
            fig = px.bar(x=accuracy, y=depts, orientation='h',
                         color=accuracy, color_continuous_scale=["#3b82f6", "#8b5cf6"])
            fig.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(style_fig(fig, 260), use_container_width=True)

        with st.container(border=True):
            st.markdown(f"#### {tr('hires_by_dept')}")
            hires = [28, 35, 42, 18]
            fig2 = px.bar(x=depts, y=hires, color=depts, color_discrete_sequence=CHART_COLORWAY)
            fig2.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig2, 260), use_container_width=True)

        with st.container(border=True):
            st.markdown(f"#### {tr('correspondence_dist')}")
            labels = ['Excellente (92%)', 'Modérée (36%)', 'Bonne (16%)', 'Faible (5%)']
            values_pie = [92.67, 36, 16, 5]
            fig4 = px.pie(values=values_pie, names=labels, hole=0.55, color_discrete_sequence=CHART_COLORWAY)
            st.plotly_chart(style_fig(fig4, 260), use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown(f"#### {tr('conversion')}")
            stages = ["Shortlistés", "Entretiens", "Offres", "Acceptées"]
            values_funnel = [310, 310, 65, 42]
            fig3 = go.Figure(go.Funnel(
                y=stages, x=values_funnel, textinfo="value+percent initial",
                marker=dict(color=["#8b5cf6", "#3b82f6", "#ec4899", "#22c55e"])
            ))
            st.plotly_chart(style_fig(fig3, 350), use_container_width=True)

    st.markdown("---")
    st.markdown(f"### {tr('market_section')}")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown(f"#### {tr('sectors_dist')}")
            sectors = api_call("GET", "/stats/sectors/distribution")
            if sectors:
                df_sectors = pd.DataFrame(sectors)
                fig = px.pie(df_sectors, values='count', names='sector', hole=0.4)
                st.plotly_chart(style_fig(fig, 350), use_container_width=True)
            else:
                st.info(tr("data_unavailable"))

    with col_b:
        with st.container(border=True):
            st.markdown(f"#### {tr('salaries_by_sector')}")
            sector_salaries = api_call("GET", "/stats/sectors/salaries")
            if sector_salaries:
                df_ss = pd.DataFrame(sector_salaries)
                fig = px.bar(df_ss, x='sector', y='avg_salary',
                             color='avg_salary', color_continuous_scale=["#3b82f6", "#8b5cf6"])
                fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-45)
                st.plotly_chart(style_fig(fig, 350), use_container_width=True)
            else:
                st.info(tr("data_unavailable"))

    col_c, col_d = st.columns(2)
    with col_c:
        with st.container(border=True):
            st.markdown(f"#### {tr('top_cities')}")
            locations = api_call("GET", "/stats/locations/top?limit=15")
            if locations:
                df_loc = pd.DataFrame(locations)
                fig = px.bar(df_loc, x='count', y='city', orientation='h',
                             color='count', color_continuous_scale='Blues')
                fig.update_layout(showlegend=False, coloraxis_showscale=False,
                                  yaxis=dict(autorange="reversed"))
                st.plotly_chart(style_fig(fig, 400), use_container_width=True)
            else:
                st.info(tr("data_unavailable"))

    with col_d:
        with st.container(border=True):
            st.markdown(f"#### {tr('remote_by_city')}")
            remote_loc = api_call("GET", "/stats/locations/remote?limit=10")
            if remote_loc:
                df_rl = pd.DataFrame(remote_loc)
                fig = px.bar(df_rl, x='city', y='remote_rate',
                             color='remote_rate', color_continuous_scale=["#f5a524", "#22c55e"])
                fig.update_layout(coloraxis_showscale=False, xaxis_tickangle=-45)
                st.plotly_chart(style_fig(fig, 400), use_container_width=True)
            else:
                st.info(tr("data_unavailable"))

    with st.container(border=True):
        st.markdown(f"#### {tr('cooccurrence')}")
        cooc = api_call("GET", "/stats/skills/cooccurrence?nrows=300")
        if cooc and cooc.get('skills'):
            df_cooc = pd.DataFrame(cooc['matrix'], index=cooc['skills'], columns=cooc['skills'])
            fig = px.imshow(df_cooc, color_continuous_scale='Purples', aspect='auto')
            fig.update_layout(height=550)
            st.plotly_chart(style_fig(fig, 550), use_container_width=True)
        else:
            st.info(tr("data_unavailable"))


def page_marche():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown(f'<div class="main-header">{tr("market_title")}</div>', unsafe_allow_html=True)
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



def page_cv():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown(f'<div class="main-header">{tr("cv_title")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="main-header">{tr("matching_title")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="main-header">{tr("reco_title")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="main-header">{tr("salary_title")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="main-header">{tr("comparator_title")}</div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="main-header">{tr("career_title")}</div>', unsafe_allow_html=True)
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
    """Appelle l'API chatbot intelligente."""
    payload = {
        "question": question,
        "profile": profile if profile else None,
        "history": [
            {"role": r, "content": m}
            for r, m in st.session_state.chat_history[-6:]
        ]
    }
    result = api_call("POST", "/chatbot/", json=payload)
    if result and "response" in result:
        return result["response"], result.get("llm_enabled", False)
    return "⚠️ Erreur du chatbot. Vérifiez que l'API est en ligne.", False



import uuid

def create_new_conversation():
    """Crée une nouvelle conversation vide."""
    conv_id = str(uuid.uuid4())[:8]
    st.session_state.conversations[conv_id] = {
        "title": "Nouvelle conversation",
        "messages": [],
        "pinned": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    st.session_state.current_conv_id = conv_id
    return conv_id


def get_current_conversation():
    """Retourne la conversation active."""
    cid = st.session_state.current_conv_id
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]
    return None


def add_message_to_current(role, content):
    """Ajoute un message à la conversation active."""
    conv = get_current_conversation()
    if conv is None:
        create_new_conversation()
        conv = get_current_conversation()
    
    conv["messages"].append({"role": role, "content": content, "ts": datetime.now().isoformat()})
    conv["updated_at"] = datetime.now().isoformat()
    
    # Auto-générer le titre à partir du premier message utilisateur
    if len(conv["messages"]) == 1 and role == "user":
        conv["title"] = content[:35] + ("..." if len(content) > 35 else "")


def delete_conversation(conv_id):
    """Supprime une conversation."""
    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]
        if st.session_state.current_conv_id == conv_id:
            st.session_state.current_conv_id = None


def toggle_pin(conv_id):
    """Épingle/désépingle une conversation."""
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["pinned"] = not st.session_state.conversations[conv_id]["pinned"]


def rename_conversation(conv_id, new_title):
    """Renomme une conversation."""
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["title"] = new_title[:50]

def page_assistant():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # ============================================================
    # INIT : Créer une conversation si aucune n'existe
    # ============================================================
    if not st.session_state.conversations:
        create_new_conversation()

    if st.session_state.current_conv_id is None:
        # Prendre la plus récente
        latest = max(st.session_state.conversations.items(),
                     key=lambda x: x[1]["updated_at"])
        st.session_state.current_conv_id = latest[0]

    # ============================================================
    # CSS POUR CHATGPT-LIKE
    # ============================================================
    st.markdown("""
    <style>
        /* Zone conversation scrollable */
        .chat-container {
            max-height: 55vh;
            overflow-y: auto;
            padding: 1rem;
            border-radius: 12px;
            background: var(--surface-2);
            border: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        
        /* Historique sidebar */
        .conv-item {
            background: var(--surface-solid);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.6rem 0.8rem;
            margin-bottom: 0.4rem;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        .conv-item:hover {
            background: var(--surface-2);
            border-color: var(--accent-1);
        }
        .conv-item.active {
            background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(236,72,153,0.1));
            border-color: var(--accent-1);
        }
        .conv-item.pinned {
            border-left: 3px solid var(--accent-2);
        }
        .conv-title {
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-1);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .conv-date {
            font-size: 0.68rem;
            color: var(--text-3);
            margin-top: 0.2rem;
        }
        
        /* Sticky input */
        .stChatInputContainer {
            position: sticky;
            bottom: 0;
            z-index: 100;
            background: var(--surface-solid);
            padding: 0.5rem;
            border-radius: 12px;
            border: 2px solid var(--accent-1) !important;
            box-shadow: 0 -4px 20px rgba(139,92,246,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # EN-TÊTE
    # ============================================================
    llm_status = api_call("GET", "/chatbot/status")
    is_ia_active = llm_status and llm_status.get("available")

    col_title, col_status, col_new = st.columns([2, 2, 1])

    with col_title:
        st.markdown(f'<div style="font-size:1.5rem; font-weight:700;">🤖 Assistant IA</div>',
                    unsafe_allow_html=True)

    with col_status:
        if is_ia_active:
            st.markdown(f"""
            <div style="background:rgba(34,197,94,0.15); border:1px solid rgba(34,197,94,0.4);
                        border-radius:8px; padding:0.4rem 0.8rem; font-size:0.75rem;
                        display:inline-block; margin-top:0.3rem;">
                <span style="display:inline-block; width:8px; height:8px; background:#22c55e;
                     border-radius:50%; margin-right:6px; animation:pulse 2s infinite;"></span>
                <b style="color:var(--success);">IA active</b>
                <span style="color:var(--text-3);"> · {llm_status.get('model', 'LLM')}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("⚠️ Mode démo")

    with col_new:
        if st.button("＋ Nouveau", key="new_conv_btn", use_container_width=True):
            create_new_conversation()
            st.rerun()

    st.markdown("---")

    # ============================================================
    # LAYOUT 2 COLONNES : Historique | Conversation
    # ============================================================
    col_history, col_chat = st.columns([1, 3])

    # ------------------------------------------------------------
    # COLONNE GAUCHE : HISTORIQUE
    # ------------------------------------------------------------
    with col_history:
        st.markdown("##### 📜 Historique")

        # Trier : épinglés en premier, puis par date
        convs = sorted(
            st.session_state.conversations.items(),
            key=lambda x: (not x[1]["pinned"], x[1]["updated_at"]),
            reverse=False,
        )
        convs = [(cid, c) for cid, c in convs]
        convs.sort(key=lambda x: (not x[1]["pinned"], -1 if False else x[1]["updated_at"]),
                   reverse=False)

        # Séparer épinglés et non-épinglés
        pinned = [(cid, c) for cid, c in st.session_state.conversations.items() if c["pinned"]]
        unpinned = [(cid, c) for cid, c in st.session_state.conversations.items() if not c["pinned"]]

        # Trier par date décroissante
        pinned.sort(key=lambda x: x[1]["updated_at"], reverse=True)
        unpinned.sort(key=lambda x: x[1]["updated_at"], reverse=True)

        # ---- Épinglés ----
        if pinned:
            st.markdown("📌 **Épinglés**")
            for cid, conv in pinned:
                is_active = (cid == st.session_state.current_conv_id)
                cls = "conv-item active pinned" if is_active else "conv-item pinned"
                st.markdown(f"""
                <div class="{cls}">
                    <div class="conv-title">📌 {conv['title']}</div>
                    <div class="conv-date">{len(conv['messages'])} messages</div>
                </div>
                """, unsafe_allow_html=True)

                # Boutons d'action
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("▶️", key=f"open_{cid}", help="Ouvrir", use_container_width=True):
                        st.session_state.current_conv_id = cid
                        st.rerun()
                with c2:
                    if st.button("📌", key=f"unpin_{cid}", help="Désépingler", use_container_width=True):
                        toggle_pin(cid)
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_{cid}", help="Supprimer", use_container_width=True):
                        delete_conversation(cid)
                        st.rerun()

        # ---- Aujourd'hui ----
        if unpinned:
            st.markdown("🕒 **Récentes**")
            for cid, conv in unpinned[:10]:
                is_active = (cid == st.session_state.current_conv_id)
                cls = "conv-item active" if is_active else "conv-item"
                st.markdown(f"""
                <div class="{cls}">
                    <div class="conv-title">{conv['title']}</div>
                    <div class="conv-date">{len(conv['messages'])} messages</div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("▶️", key=f"open2_{cid}", help="Ouvrir", use_container_width=True):
                        st.session_state.current_conv_id = cid
                        st.rerun()
                with c2:
                    if st.button("📌", key=f"pin_{cid}", help="Épingler", use_container_width=True):
                        toggle_pin(cid)
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del2_{cid}", help="Supprimer", use_container_width=True):
                        delete_conversation(cid)
                        st.rerun()

    # ------------------------------------------------------------
    # COLONNE DROITE : CONVERSATION
    # ------------------------------------------------------------
    with col_chat:
        conv = get_current_conversation()
        if conv is None:
            st.info("Aucune conversation. Cliquez sur **＋ Nouveau**.")
            return

        # Titre de la conversation
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.markdown(f"#### 💬 {conv['title']}")
        with col_t2:
            if st.button("📤 Exporter", key="export_conv", use_container_width=True):
                txt = "\n\n".join([f"{'👤 Vous' if m['role']=='user' else '🤖 IA'}: {m['content']}"
                                    for m in conv["messages"]])
                st.download_button("📥 Télécharger", txt,
                                   file_name=f"chat_{conv['title'][:20]}.txt",
                                   mime="text/plain", key="dl_conv")

        # ---- Zone de messages ----
        if not conv["messages"]:
            # Message de bienvenue
            st.markdown("""
            <div style="text-align:center; padding:2rem 1rem; color:var(--text-2);">
                <div style="font-size:3rem;">🤖</div>
                <h3 style="color:var(--text-1); margin-top:0.5rem;">Bonjour ! Comment puis-je vous aider ?</h3>
                <p style="color:var(--text-3);">Posez-moi une question sur les compétences, les salaires, votre CV, les entretiens...</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in conv["messages"]:
                with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                    st.markdown(msg["content"])

    # ============================================================
    # ZONE DE SAISIE FIXE (pleine largeur en bas)
    # ============================================================
    user_input = st.chat_input("💬 Posez votre question à l'IA...")

    if user_input:
        # Ajouter le message utilisateur
        add_message_to_current("user", user_input)

        # Appeler le LLM
        with st.spinner("🤔 L'IA réfléchit..."):
            result = chatbot_api(
                question=user_input,
                profile=st.session_state.cv_profile,
                history=[
                    {"role": m["role"], "content": m["content"]}
                    for m in get_current_conversation()["messages"][-6:]
                ]
            )
            response = result.get("response", "Erreur") if result else "Erreur"

        add_message_to_current("assistant", response)
        st.rerun()

def page_rapport():
    st.caption(f"📅 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown(f'<div class="main-header">{tr("report_title")}</div>', unsafe_allow_html=True)
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
    now = datetime.now()
    st.markdown(f"""
    <div style="margin-bottom: 0.5rem;">
        <span style="font-family:'Sora',sans-serif; font-size:1.5rem; font-weight:800;
             background: linear-gradient(135deg, #8b5cf6, #ec4899);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">JobPulseAI</span>
    </div>
    <p style="color:var(--text-3); font-size:0.9rem; line-height:1.6; max-width:300px;">
        AI-Powered Career Intelligence · Aide les talents à trouver leur voie et les entreprises à recruter plus intelligemment.
    </p>
    <div style="margin-top:0.5rem; font-size:0.8rem; color:var(--text-3);">
        MMXXVI · JobPulseAI Co. · Public Benefit Co.
    </div>
    <div style="margin-top:0.5rem; font-size:0.75rem; color:var(--accent-1); font-weight:600;">
        🕒 {now.strftime('%d/%m/%Y %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)
    
with cols[1]:
    st.markdown(f"**{tr('product')}**")
    if st.button("Home", key="footer_home", use_container_width=True):
        st.session_state["nav"] = "🏠 Accueil"
        st.rerun()
    if st.button("Marché" if st.session_state.language == "FR" else "Market", key="footer_market", use_container_width=True):
        st.session_state["nav"] = "📈 Marché"
        st.rerun()
    if st.button("CV", key="footer_cv", use_container_width=True):
        st.session_state["nav"] = "📄 CV"
        st.rerun()
    if st.button("Matching", key="footer_matching", use_container_width=True):
        st.session_state["nav"] = "🤝 Matching"
        st.rerun()
    if st.button(tr("page_recommendations").replace("🎯 ", ""), key="footer_reco", use_container_width=True):
        st.session_state["nav"] = "🎯 Recommandations"
        st.rerun()

with cols[2]:
    st.markdown(f"**{tr('updates')}**")
    st.caption(tr("privacy"))
    email = st.text_input(tr("email_placeholder"), placeholder=tr("email_placeholder"),
                          key="footer_email", label_visibility="collapsed")
    if st.button(tr("subscribe"), key="footer_subscribe", use_container_width=True):
        if email:
            st.success(f"✅ Merci {email} !" if st.session_state.language == "FR" else f"✅ Thanks {email}!")
        else:
            st.warning("Email requis" if st.session_state.language == "FR" else "Email required")

st.markdown("---")
col_left, col_right = st.columns([2, 1])
with col_left:
    st.caption(tr("all_rights"))
with col_right:
    st.markdown("""
    <div style="display:flex; gap:0.8rem; justify-content:flex-end; font-size:1.1rem;">
        <a href="#" style="color:var(--text-3); text-decoration:none;">🔗</a>
        <a href="#" style="color:var(--text-3); text-decoration:none;">🐦</a>
        <a href="#" style="color:var(--text-3); text-decoration:none;">💼</a>
        <a href="#" style="color:var(--text-3); text-decoration:none;">📺</a>
    </div>
    """, unsafe_allow_html=True)
