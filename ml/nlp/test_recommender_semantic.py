# ml/nlp/test_recommender_semantic.py
from ml.nlp.recommender import load_jobs, recommend_jobs

print("📂 Chargement des offres...")
jobs = load_jobs("data/processed/postings_sample_50000.csv", sample_size=200)

# Profil test
profile = {
    "skills": ["python", "machine learning", "tensorflow", "sql", "pandas"],
    "cv_text": (
        "Data scientist avec 3 ans d'expérience. "
        "Maîtrise de Python, TensorFlow, scikit-learn, SQL. "
        "Expérience en machine learning et deep learning."
    ),
}

print(f"\n🔍 Recherche sur {len(jobs)} offres...")
recs = recommend_jobs(profile, jobs, top_n=5)

print("\n" + "=" * 70)
print("TOP 5 RECOMMANDATIONS (avec matching sémantique)")
print("=" * 70)

for i, r in enumerate(recs, 1):
    print(f"\n{i}. {r['title']} — {r['company']}")
    print(f"   📍 {r['location']}")
    print(f"   🎯 Score final : {r['score']}%")
    print(f"      • Compétences : {r['skill_score']}%")
    print(f"      • Sémantique  : {r['semantic_score']}%")
    print(f"   ✅ Communes : {', '.join(r['common_skills'][:5])}")
    print(f"   ❌ Manquantes : {', '.join(r['missing_skills'][:5])}")