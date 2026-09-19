# ml/tests/test_recommender.py
# Test du système de recommandation

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.recommender import load_jobs, recommend_jobs
from nlp.resume_analyzer import analyze_resume

def test_recommend():
    # Charger un petit échantillon d'offres (100 lignes pour le test)
    jobs_path = os.path.join("data", "processed", "postings_sample_50000.csv")
    if not os.path.exists(jobs_path):
        print("⚠️ Fichier d'offres introuvable. Utilisation d'un échantillon vide pour le test.")
        return

    jobs_df = load_jobs(jobs_path, sample_size=100)
    if jobs_df.empty:
        print("⚠️ Aucune offre chargée.")
        return

    # Analyser le CV exemple
    cv_path = os.path.join("data", "cv_samples", "Resume.pdf")
    if not os.path.exists(cv_path):
        print("⚠️ CV exemple introuvable.")
        return

    profile = analyze_resume(cv_path)

    # Recommander les 5 meilleures offres
    recommendations = recommend_jobs(profile, jobs_df, top_n=5)

    print("✅ Test recommandation réussi.")
    print(f"Nombre de recommandations : {len(recommendations)}")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']} chez {rec['company']}")
        print(f"   Score : {rec['score']}%")
        print(f"   Compétences communes : {rec['common_skills']}")
        print(f"   Compétences manquantes : {rec['missing_skills'][:5]}...")  # tronqué

if __name__ == "__main__":
    test_recommend()