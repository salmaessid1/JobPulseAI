# backend/app/services/recommendation_service.py
import os
import sys
import traceback
import pandas as pd
import math
from typing import Dict, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

from ml.nlp.recommender import recommend_jobs

_JOBS_CACHE = None


def load_jobs_data():
    global _JOBS_CACHE
    if _JOBS_CACHE is not None:
        return _JOBS_CACHE

    # 1) Échantillon embarqué (pour Render)
    embedded_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'data', 'postings_render.csv'
    ))

    # 2) Échantillon local
    sample_path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")

    # 3) Fichier brut local
    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")

    print(f"🔍 Embedded : {embedded_path} -> {os.path.exists(embedded_path)}")
    print(f"🔍 Sample   : {sample_path} -> {os.path.exists(sample_path)}")
    print(f"🔍 Raw      : {raw_path} -> {os.path.exists(raw_path)}")

    if os.path.exists(embedded_path):
        file_path = embedded_path
        nrows = 500
        print("📌 Utilisation de l'échantillon embarqué (Render)")
    elif os.path.exists(sample_path):
        file_path = sample_path
        nrows = 1000
        print("📌 Utilisation de l'échantillon local")
    elif os.path.exists(raw_path):
        file_path = raw_path
        nrows = 500
        print("📌 Utilisation du fichier brut local")
    else:
        raise FileNotFoundError(
            f"Aucun fichier d'offres trouvé.\n"
            f"Chemins testés :\n  - {embedded_path}\n  - {sample_path}\n  - {raw_path}"
        )

    print(f"📂 Chargement : {file_path}")
    _JOBS_CACHE = pd.read_csv(file_path, nrows=nrows, low_memory=False)
    print(f"✅ {len(_JOBS_CACHE)} offres chargées et mises en cache")
    return _JOBS_CACHE


def _to_native(v):
    if v is None:
        return ""
    if isinstance(v, (int, float, str, bool)):
        return v
    if hasattr(v, "item"):
        return v.item()
    if isinstance(v, float) and math.isnan(v):
        return ""
    return str(v)


def clean_recommendation(rec: Dict) -> Dict:
    return {
        "job_id": str(_to_native(rec.get("job_id", ""))),
        "title": str(_to_native(rec.get("title", "Offre inconnue"))),
        "company": str(_to_native(rec.get("company", "Entreprise inconnue"))),
        "location": str(_to_native(rec.get("location", ""))),
        "score": float(_to_native(rec.get("score", 0))),
        "common_skills": [str(s) for s in rec.get("common_skills", [])],
        "missing_skills": [str(s) for s in rec.get("missing_skills", [])],
        "extra_skills": [str(s) for s in rec.get("extra_skills", [])],
        "cv_skills_count": int(_to_native(rec.get("cv_skills_count", 0))),
        "job_skills_count": int(_to_native(rec.get("job_skills_count", 0))),
        "common_count": int(_to_native(rec.get("common_count", 0))),
    }


def get_recommendations(profile: Dict, top_n: int = 10) -> List[Dict]:
    try:
        jobs_df = load_jobs_data()
        if jobs_df.empty:
            return []
        print(f"🔍 Recherche pour profil : {profile.get('skills', [])[:5]}...")
        recs = recommend_jobs(profile, jobs_df, top_n)
        print(f"✅ {len(recs)} recommandations générées")
        return [clean_recommendation(r) for r in recs]
    except Exception as e:
        print("❌ EXCEPTION dans get_recommendations :")
        traceback.print_exc()
        raise Exception(f"Erreur recommandations : {str(e)}")


def get_cached_stats():
    global _JOBS_CACHE
    if _JOBS_CACHE is None:
        return {"cached": False}
    return {
        "cached": True,
        "total_jobs": len(_JOBS_CACHE),
        "columns": list(_JOBS_CACHE.columns),
    }