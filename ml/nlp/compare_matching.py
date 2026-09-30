# ml/nlp/compare_matching.py
"""
Compare le matching classique (mots-clés) avec le matching sémantique.
Produit un graphique pour le rapport.
"""
import matplotlib.pyplot as plt
import numpy as np
from ml.nlp.job_matcher import match_cv_job
from ml.nlp.semantic_matcher import hybrid_match

# Exemples de test (CV, Offre, compétences CV, compétences offre)
EXAMPLES = [
    {
        "name": "Match évident",
        "cv_text": "Data scientist avec Python et TensorFlow.",
        "job_text": "Ingénieur IA Python avec expérience en deep learning.",
        "cv_skills": ["python", "tensorflow", "machine learning"],
        "job_skills": ["python", "deep learning", "pytorch"],
    },
    {
        "name": "Synonymes (mots-clés échoue)",
        "cv_text": "Développeur logiciel spécialisé en programmation Python.",
        "job_text": "Nous recrutons un ingénieur pour coder en Python.",
        "cv_skills": ["python"],
        "job_skills": ["python", "coding"],
    },
    {
        "name": "Contexte similaire",
        "cv_text": "Expert en analyse de données et statistiques appliquées.",
        "job_text": "Poste de Data Scientist pour modéliser des données massives.",
        "cv_skills": ["statistics", "data analysis"],
        "job_skills": ["data science", "machine learning"],
    },
    {
        "name": "Match partiel",
        "cv_text": "Développeur web front-end HTML CSS JavaScript.",
        "job_text": "Full-stack developer Python React MySQL.",
        "cv_skills": ["javascript", "html", "css"],
        "job_skills": ["python", "react", "mysql", "javascript"],
    },
    {
        "name": "Aucun rapport",
        "cv_text": "Chef cuisinier avec 10 ans en restauration gastronomique.",
        "job_text": "Ingénieur DevOps Kubernetes Docker AWS.",
        "cv_skills": ["cooking", "management"],
        "job_skills": ["kubernetes", "docker", "aws"],
    },
]

# Calcul des deux scores
classic_scores = []
semantic_scores = []
labels = []

for ex in EXAMPLES:
    # Matching classique
    result_classic = match_cv_job(ex["cv_skills"], ex["job_skills"])
    classic_scores.append(result_classic["score"])

    # Matching hybride
    result_hybrid = hybrid_match(
        ex["cv_skills"], ex["job_skills"], ex["cv_text"], ex["job_text"]
    )
    semantic_scores.append(result_hybrid["final_score"])
    labels.append(ex["name"])

# ============================================================
# GRAPHIQUE
# ============================================================
x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width / 2, classic_scores, width, label="Matching classique (mots-clés)", color="#ec4899")
bars2 = ax.bar(x + width / 2, semantic_scores, width, label="Matching sémantique (Sentence-BERT)", color="#8b5cf6")

# Ajouter les valeurs sur les barres
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.0f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9)

ax.set_ylabel("Score de matching (%)", fontsize=12)
ax.set_title("Comparaison : Matching classique vs Sémantique", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=15, ha="right")
ax.legend(loc="upper right")
ax.set_ylim(0, 110)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("reports/semantic_vs_classic.png", dpi=150, bbox_inches="tight")
print("✅ Graphique sauvegardé : reports/semantic_vs_classic.png")
plt.show()