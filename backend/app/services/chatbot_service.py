# backend/app/services/chatbot_service.py
import os
import sys
from typing import Dict, List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

try:
    # On utilise le même client que pour OpenAI
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# ⚠️ On utilise la clé de Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ⚠️ Le point crucial : l'URL de base de l'API de Groq
GROQ_API_BASE = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT = """Tu es un assistant carrière expert pour JobPulseAI.
Tu aides les candidats à :
- Comprendre les compétences demandées sur le marché
- Améliorer leur CV
- Trouver les formations adaptées
- Naviguer dans les métiers de la Data Science
- Comprendre les salaires

Réponds toujours en français, de manière concise et structurée.
Utilise des emojis pour rendre les réponses plus lisibles."""


def get_chatbot_response(question: str, profile: Optional[Dict] = None, history: Optional[List[Dict]] = None) -> Dict:
    # Fallback si la clé n'est pas configurée
    if not LANGCHAIN_AVAILABLE or not GROQ_API_KEY:
        return {"response": _fallback_response(question, profile), "source": "fallback", "llm_enabled": False}
    
    try:
        context = ""
        if profile:
            skills = profile.get('skills', [])
            domains = profile.get('domains', [])
            seniority = profile.get('seniority', 'inconnu')
            context = f"\n\nContexte du candidat :\n- Compétences : {', '.join(skills[:10])}\n- Domaines : {', '.join(domains)}\n- Séniorité : {seniority}"
        
        messages = [SystemMessage(content=SYSTEM_PROMPT + context)]
        if history:
            for msg in history[-5:]:
                messages.append(HumanMessage(content=msg["content"]) if msg.get("role") == "user" else AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=question))
        
        # ⚠️ Configuration du LLM pour Groq
        llm = ChatOpenAI(
            model="llama-3.3-70b-versatile", # Un des meilleurs modèles gratuits de Groq
            temperature=0.7,
            api_key=GROQ_API_KEY,          # On utilise la clé Groq
            base_url=GROQ_API_BASE,        # On redirige vers l'API de Groq
        )
        
        response = llm.invoke(messages)
        
        return {"response": response.content, "source": "groq", "llm_enabled": True}
    except Exception as e:
        return {"response": f"⚠️ Erreur LLM : {str(e)}\n\n{_fallback_response(question, profile)}", "source": "error", "llm_enabled": False}

# ... Le reste du fichier (_fallback_response, is_llm_available) reste identique
def _fallback_response(question: str, profile: Optional[Dict] = None) -> str:
    """Réponse de secours si OpenAI n'est pas disponible."""
    q = question.lower()
    
    if "compétence" in q or "skill" in q:
        return "💡 **Compétences demandées en 2026**\n\n" \
               "🔹 Data Science : Python, SQL, ML, Deep Learning\n" \
               "🔹 Cloud : AWS, Azure, Docker, Kubernetes\n" \
               "🔹 Dev : JavaScript, TypeScript, React"
    elif "salaire" in q:
        return "💰 **Salaires moyens (USA, 2026)**\n\n" \
               "• Data Scientist : 95 000 – 130 000 USD\n" \
               "• ML Engineer : 110 000 – 150 000 USD\n" \
               "• Data Engineer : 100 000 – 140 000 USD"
    elif "cv" in q:
        return "📄 **Conseils CV**\n\n" \
               "1. En-tête avec nom et contact\n" \
               "2. Résumé percutant (2-3 lignes)\n" \
               "3. Compétences clés en colonnes\n" \
               "4. Expériences chiffrées\n" \
               "5. Formations et projets"
    else:
        return "🤖 Assistant carrière JobPulseAI. Posez-moi des questions sur les compétences, salaires, CV, ou métiers de la Data."


def is_llm_available() -> bool:
    """Vérifie si le LLM est disponible."""
    return LANGCHAIN_AVAILABLE and bool(GROQ_API_KEY)