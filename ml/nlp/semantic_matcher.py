# ml/nlp/semantic_matcher.py
"""
Matching sémantique CV <-> Offre avec Sentence-BERT.
Combine deux scores :
  - Score "compétences" : proportion de compétences communes (0-100)
  - Score "sémantique"  : similarité cosinus entre les embeddings (0-100)
Le score final est une pondération des deux.
"""
from sentence_transformers import SentenceTransformer, util
import torch

# ============================================================
# MODEL (chargé une seule fois)
# ============================================================
_model = None
MODEL_NAME = "all-MiniLM-L6-v2"


def get_model():
    """Charge le modèle Sentence-BERT (lazy loading)."""
    global _model
    if _model is None:
        print(f"🔄 Chargement du modèle {MODEL_NAME}...")
        _model = SentenceTransformer(MODEL_NAME)
        print("✅ Modèle chargé")
    return _model


# ============================================================
# SIMILARITÉ SÉMANTIQUE
# ============================================================
def semantic_similarity(cv_text: str, job_text: str) -> float:
    """
    Calcule la similarité sémantique entre deux textes.
    Retourne un score entre 0 et 100.
    """
    if not cv_text or not job_text:
        return 0.0

    model = get_model()
    emb_cv = model.encode(cv_text, convert_to_tensor=True)
    emb_job = model.encode(job_text, convert_to_tensor=True)

    sim = util.pytorch_cos_sim(emb_cv, emb_job).item()
    # Cosinus est entre -1 et 1 → on ramène à 0-100
    score = max(0.0, sim) * 100
    return round(score, 2)


# ============================================================
# MATCHING HYBRIDE
# ============================================================
def hybrid_match(
    cv_skills,
    job_skills,
    cv_text: str = "",
    job_text: str = "",
    weight_skills: float = 0.6,
    weight_semantic: float = 0.4,
) -> dict:
    """
    Combine matching par compétences + matching sémantique.

    Args:
        cv_skills : liste de compétences du CV
        job_skills : liste de compétences de l'offre
        cv_text : texte brut du CV
        job_text : texte brut de l'offre
        weight_skills : poids du score compétences (défaut 0.6)
        weight_semantic : poids du score sémantique (défaut 0.4)

    Returns:
        dict avec final_score, skill_score, semantic_score, common/missing skills.
    """
    # --- Score 1 : compétences communes ---
    cv_set = set(s.lower().strip() for s in cv_skills if s)
    job_set = set(s.lower().strip() for s in job_skills if s)

    common = cv_set & job_set
    missing = job_set - cv_set
    extra = cv_set - job_set

    skill_score = (len(common) / len(job_set) * 100) if job_set else 0.0

    # --- Score 2 : sémantique ---
    semantic_score = 0.0
    if cv_text and job_text:
        semantic_score = semantic_similarity(cv_text, job_text)

    # --- Score final ---
    if semantic_score > 0:
        final_score = (weight_skills * skill_score) + (weight_semantic * semantic_score)
    else:
        # Pas de texte → on utilise uniquement les compétences
        final_score = skill_score

    return {
        "final_score": round(final_score, 2),
        "skill_score": round(skill_score, 2),
        "semantic_score": round(semantic_score, 2),
        "common_skills": sorted(common),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
        "cv_skills_count": len(cv_set),
        "job_skills_count": len(job_set),
        "common_count": len(common),
    }


# ============================================================
# TEST DIRECT
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MATCHING SÉMANTIQUE")
    print("=" * 60)

    cv_text = "Data scientist with expertise in Python, machine learning, TensorFlow and NLP."
    job_text = "Looking for an AI engineer to work on deep learning models with PyTorch."

    print("\n📄 CV :", cv_text)
    print("📋 Offre :", job_text)

    score = semantic_similarity(cv_text, job_text)
    print(f"\n🎯 Similarité sémantique : {score}%")

    # Test matching hybride
    cv_skills = ["python", "machine learning", "tensorflow"]
    job_skills = ["python", "pytorch", "deep learning"]

    result = hybrid_match(cv_skills, job_skills, cv_text, job_text)
    print("\n🔬 Matching hybride :")
    for k, v in result.items():
        print(f"   {k} : {v}")