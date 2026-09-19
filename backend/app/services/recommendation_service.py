# backend/app/services/recommendation_service.py
import os
import sys
import pandas as pd
import math
from typing import Dict, List
from functools import lru_cache

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

from ml.nlp.recommender import recommend_jobs

# Cache global pour les jobs
_JOBS_CACHE = None
_JOBS_SKILLS_CACHE = None  # Pré-calcul des compétences


def load_jobs_data():
    """Charge les jobs UNE SEULE FOIS et les met en cache."""
    global _JOBS_CACHE
    if _JOBS_CACHE is not None:
        return _JOBS_CACHE

    sample_path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")
    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")

    if os.path.exists(sample_path):
        file_path = sample_path
        nrows = 1000  # Réduire pour accélérer
    elif os.path.exists(raw_path):
        file_path = raw_path
        nrows = 500   # Réduire pour accélérer
    else:
        raise FileNotFoundError("Aucun fichier d'offres trouvé")

    print(f"📂 Chargement des offres depuis : {file_path}")
    _JOBS_CACHE = pd.read_csv(file_path, nrows=nrows, low_memory=False)
    print(f"✅ {len(_JOBS_CACHE)} offres chargées et mises en cache")
    return _JOBS_CACHE


def clean_value(value, default=""):
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    if isinstance(value, int):
        return str(value)
    return str(value)


def clean_recommendation(rec: Dict) -> Dict:
    rec['job_id'] = clean_value(rec.get('job_id'), "")
    rec['title'] = clean_value(rec.get('title'), "Offre inconnue")
    rec['company'] = clean_value(rec.get('company'), "Entreprise inconnue")
    rec['location'] = clean_value(rec.get('location'), "")
    return rec


def get_recommendations(profile: Dict, top_n: int = 10) -> List[Dict]:
    try:
        jobs_df = load_jobs_data()
        if jobs_df.empty:
            return []
        recs = recommend_jobs(profile, jobs_df, top_n)
        return [clean_recommendation(r) for r in recs]
    except Exception as e:
        raise Exception(f"Erreur recommandations : {str(e)}")


def get_cached_stats():
    """Retourne des stats rapides sur le cache."""
    global _JOBS_CACHE
    if _JOBS_CACHE is None:
        return {"cached": False}
    return {
        "cached": True,
        "total_jobs": len(_JOBS_CACHE),
        "columns": list(_JOBS_CACHE.columns)
    }