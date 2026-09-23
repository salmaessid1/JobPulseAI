# backend/app/services/chatbot_service.py
"""
Service chatbot intelligent propulsé par Groq (Llama 3.3 70B).
Fallback local si Groq n'est pas configuré.
"""
import os
import sys
from typing import Dict, List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

# Charger .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, "backend", ".env"))
except ImportError:
    pass

# Essayer d'importer LangChain
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"  # Meilleur modèle gratuit Groq (120B params)

# ============================================================
# PROMPT SYSTÈME
# ============================================================
SYSTEM_PROMPT = """Tu es **JobPulseAI**, un assistant carrière expert, intelligent et bienveillant.

## Ton rôle
Tu aides les candidats, étudiants et professionnels à :
- Comprendre le marché de l'emploi et ses tendances
- Analyser et améliorer leur CV
- Identifier les compétences à acquérir (skill gap)
- Trouver les meilleures offres d'emploi correspondant à leur profil
- Négocier leur salaire et comprendre les fourchettes
- Se préparer aux entretiens
- Choisir des formations et certifications pertinentes
- Naviguer dans les métiers de la Data Science, IA, Tech

## Règles de réponse
1. Réponds TOUJOURS en français, sauf si l'utilisateur écrit dans une autre langue
2. Sois CONCIS mais complet (2-4 paragraphes max, sauf demande explicite)
3. Utilise des **emojis** et du **markdown** pour la lisibilité
4. Structure tes réponses avec des titres et des listes à puces
5. Si tu ne sais pas, dis-le honnêtement
6. N'invente JAMAIS de statistiques ou de faits
7. Termine par une question ou une suggestion pour engager la conversation
8. Reste professionnel, encourageant et positif

## Format de réponse
Utilise ce format quand c'est pertinent :
- 📌 **Titre du sujet**
- Points clés avec puces
- 💡 **Conseil** pour terminer
"""


# ============================================================
# FONCTION PRINCIPALE
# ============================================================
def get_chatbot_response(
    question: str,
    profile: Optional[Dict] = None,
    history: Optional[List[Dict]] = None,
) -> Dict:
    """Génère une réponse intelligente via Groq ou fallback."""
    
    # Si Groq n'est pas configuré → fallback
    if not LANGCHAIN_AVAILABLE or not GROQ_API_KEY:
        return {
            "response": _fallback_response(question, profile),
            "source": "fallback",
            "llm_enabled": False,
        }
    
    try:
        # Ajouter le contexte du profil si disponible
        context = ""
        if profile:
            name = profile.get('name', 'Candidat')
            skills = profile.get('skills', [])
            domains = profile.get('domains', [])
            seniority = profile.get('seniority', 'non défini')
            context = f"""

## Contexte du candidat
- Nom : {name}
- Compétences ({len(skills)}) : {', '.join(skills[:15]) if skills else 'aucune'}
- Domaines : {', '.join(domains) if domains else 'non défini'}
- Séniorité : {seniority}

Utilise ce contexte pour personnaliser tes réponses quand c'est pertinent."""

        # Construire les messages
        messages = [SystemMessage(content=SYSTEM_PROMPT + context)]
        
        if history:
            for msg in history[-6:]:  # 6 derniers messages (3 échanges)
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        messages.append(HumanMessage(content=question))
        
        # Liste de modèles de secours (par ordre de préférence)
        models_to_try = [
            GROQ_MODEL,              # Modèle principal (openai/gpt-oss-120b)
            "openai/gpt-oss-20b",    # Fallback 1
            "qwen/qwen3.8-27b",      # Fallback 2
        ]
        
        last_error = None
        response = None
        
        for model_name in models_to_try:
            try:
                llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.7,
                    max_tokens=1024,
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_API_BASE,
                )
                response = llm.invoke(messages)
                print(f"✅ Réponse générée avec {model_name}")
                break
            except Exception as e:
                last_error = e
                print(f"⚠️ Modèle {model_name} échoué, essai du suivant...")
                continue
        
        if response is None:
            raise last_error or Exception("Tous les modèles ont échoué")
        
        return {
            "response": response.content,
            "source": "groq",
            "llm_enabled": True,
        }
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__} : {str(e)}"
        print(f"🔴 ERREUR CHATBOT : {error_detail}")
        traceback.print_exc()
        return {
            "response": f"⚠️ **Erreur LLM** : `{error_detail}`\n\n{_fallback_response(question, profile)}",
            "source": "error",
            "llm_enabled": False,
        }


# ============================================================
# FALLBACK (si pas de clé API ou erreur)
# ============================================================
def _fallback_response(question: str, profile: Optional[Dict] = None) -> str:
    """Réponses prédéfinies intelligentes quand Groq n'est pas dispo."""
    q = question.lower().strip()
    
    # Salutations
    if any(w in q for w in ["bonjour", "salut", "hello", "hi", "coucou"]):
        return "👋 **Bonjour !**\n\nJe suis JobPulseAI, votre assistant carrière. Posez-moi une question sur les compétences, les salaires, votre CV, les métiers de la Data, les entretiens...\n\n💡 **Exemple :** _Quelles compétences pour devenir Data Scientist ?_"
    
    # Compétences
    if any(w in q for w in ["compétence", "skill", "apprendre", "maîtriser"]):
        return """💡 **Compétences les plus demandées en 2026**

🔹 **Data Science & IA**
Python, SQL, Machine Learning, Deep Learning, NLP, Computer Vision

🔹 **Cloud & DevOps**
AWS, Azure, GCP, Docker, Kubernetes, Terraform

🔹 **Développement**
JavaScript, TypeScript, React, Node.js, FastAPI

🔹 **Data Engineering**
Spark, Kafka, Airflow, dbt, Snowflake

📚 **Conseil :** Commencez par Python + SQL, puis spécialisez-vous selon votre domaine cible."""
    
    # Salaire
    if any(w in q for w in ["salaire", "rémunération", "paie", "gagner"]):
        return """💰 **Fourchettes salariales (USA, 2026)**

| Métier | Junior | Senior |
|--------|--------|--------|
| Data Scientist | 80-100k$ | 130-180k$ |
| ML Engineer | 90-120k$ | 150-200k$ |
| Data Engineer | 85-110k$ | 140-180k$ |
| Data Analyst | 60-80k$ | 90-120k$ |

📌 **Facteurs influençant :** localisation, entreprise (FAANG vs startup), expérience, compétences rares.

💡 **Conseil :** Utilisez la page **💰 Salaire** du dashboard pour une estimation personnalisée."""
    
    # CV
    if any(w in q for w in ["cv", "resume", "candidature"]):
        return """📄 **Conseils pour un CV remarquable**

✅ **Structure gagnante**
1. En-tête (nom, email, LinkedIn, GitHub)
2. Résumé professionnel (2-3 lignes percutantes)
3. Compétences clés (colonnes par catégorie)
4. Expériences avec **résultats chiffrés**
5. Formations et certifications
6. Projets personnels (GitHub, Kaggle)

❌ **À éviter**
- Fautes d'orthographe
- Trop de couleurs / design chargé
- Objectifs vagues ("je veux progresser")
- Absence de chiffres

💡 **Astuce :** Adaptez votre CV à chaque offre en mettant en avant les compétences clés de l'annonce."""
    
    # Entretien
    if any(w in q for w in ["entretien", "interview", "recrutement"]):
        return """🎤 **Préparation aux entretiens**

📌 **Étapes clés**
1. **Recherche** : étudiez l'entreprise (site, LinkedIn, actualités)
2. **Technique** : révisez vos fondamentaux (algorithmes, stats, SQL, Python)
3. **Comportemental** : préparez la méthode **STAR** (Situation, Tâche, Action, Résultat)
4. **Questions** : préparez 3-5 questions à poser

💡 **Conseil :** Entraînez-vous à voix haute. Utilisez Pramp ou Interviewing.io pour des mock interviews."""
    
    # Métiers
    if any(w in q for w in ["métier", "carrière", "job", "poste"]):
        return """🚀 **Métiers de la Data & IA**

🔹 **Data Scientist** → modélisation, IA, statistiques
🔹 **ML Engineer** → déploiement, MLOps, production
🔹 **Data Engineer** → pipelines, ETL, big data
🔹 **Data Analyst** → reporting, BI, visualisation
🔹 **AI Research Scientist** → recherche, publications

📌 **Comment choisir ?**
- Vous aimez analyser → **Data Analyst**
- Vous aimez construire → **Data Engineer**
- Vous aimez modéliser → **Data Scientist**
- Vous aimez déployer → **ML Engineer**

💡 **Conseil :** Testez plusieurs rôles via des projets personnels avant de vous spécialiser."""
    
    # Formation
    if any(w in q for w in ["formation", "certification", "cours"]):
        return """🎓 **Formations & Certifications recommandées**

🔹 **Cours en ligne**
- Coursera (IBM, Stanford, DeepLearning.AI)
- Udemy (Python, ML, Deep Learning)
- DataCamp (interactif, orienté pratique)
- fast.ai (Deep Learning gratuit)

🔹 **Certifications valorisées**
- AWS Certified Machine Learning
- Google Professional Data Engineer
- Microsoft Azure AI Engineer
- TensorFlow Developer Certificate

💡 **Conseil :** Privilégiez les projets pratiques aux certifications. Un bon GitHub vaut plus qu'un certificat."""
    
    # Salaire négociation
    if any(w in q for w in ["négociation", "négocier"]):
        return """💼 **Négociation salariale**

📌 **Préparation**
1. Renseignez-vous sur les fourchettes (Glassdoor, Levels.fyi)
2. Définissez votre **salaire cible**, **acceptable** et **minimum**
3. Préparez vos arguments (compétences rares, réalisations chiffrées)

🎯 **Techniques**
- Laissez l'entreprise donner une fourchette en premier
- Ne dites jamais "je suis flexible"
- Négociez aussi : télétravail, formation, bonus, congés

💡 **Conseil :** Une augmentation de 10-15% est courante lors d'une négociation bien menée."""
    
    # Merci
    if any(w in q for w in ["merci", "thanks", "super"]):
        return "🙏 **Avec plaisir !** N'hésitez pas si vous avez d'autres questions. Bonne chance dans votre recherche !"
    
    # Défaut
    return f"""🤖 **Je suis JobPulseAI, votre assistant carrière.**

Je peux vous aider sur :
- 🎯 Les **compétences** à acquérir
- 💰 Les **salaires** par métier
- 📄 L'optimisation de votre **CV**
- 🎤 La préparation aux **entretiens**
- 🚀 Les **métiers** de la Data & Tech
- 🎓 Les **formations** et certifications

📌 **Posez-moi une question précise**, par exemple :
> _"Quelles compétences pour devenir ML Engineer ?"_

💡 **Note :** Pour des réponses vraiment intelligentes, configurez la clé `GROQ_API_KEY` dans le fichier `.env` du backend."""


# ============================================================
# UTILITAIRES
# ============================================================
def is_llm_available() -> bool:
    """Vérifie si le LLM est disponible."""
    return LANGCHAIN_AVAILABLE and bool(GROQ_API_KEY)


def get_llm_status() -> Dict:
    """Statut détaillé du LLM."""
    if not LANGCHAIN_AVAILABLE:
        return {
            "available": False,
            "reason": "LangChain non installé. Exécutez : pip install langchain langchain-openai",
        }
    if not GROQ_API_KEY:
        return {
            "available": False,
            "reason": "Clé GROQ_API_KEY manquante dans .env. Obtenez-en une sur https://console.groq.com",
        }
    return {
        "available": True,
        "provider": "Groq",
        "model": GROQ_MODEL,
    }