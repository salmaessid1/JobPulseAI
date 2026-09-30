# ml/nlp/recommender.py
"""
Recommender qui utilise le matching hybride (compétences + sémantique).
"""
import pandas as pd
from typing import List, Dict, Optional
from .extract_skills import extract_skills
from .job_matcher import match_cv_job
from .semantic_matcher import hybrid_match


def load_jobs(file_path: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=42)
    return df


def extract_job_skills_from_row(row: pd.Series) -> List[str]:
    text = row.get("description", "")
    if pd.isna(text) or not str(text).strip():
        text = row.get("skills_desc", "")
    if pd.isna(text) or not str(text).strip():
        return []
    result = extract_skills(text)
    return result["skills"]


def recommend_jobs(
    profile: Dict,
    jobs_df: pd.DataFrame,
    top_n: int = 10,
    use_semantic: bool = True,
) -> List[Dict]:
    """
    Recommande les offres les plus pertinentes pour un profil.
    
    Args:
        profile : dict avec 'skills' et éventuellement 'cv_text'
        jobs_df : DataFrame des offres
        top_n : nombre de recommandations
        use_semantic : si True, utilise le matching sémantique
    """
    cv_skills = profile.get("skills", [])
    cv_text = profile.get("cv_text", "")

    if not cv_skills and not cv_text:
        return []

    recommendations = []
    total = len(jobs_df)

    for idx, row in jobs_df.iterrows():
        job_skills = extract_job_skills_from_row(row)
        if not job_skills and not cv_text:
            continue

        # Texte de l'offre (titre + description)
        job_text = ""
        title = str(row.get("title", ""))
        desc = str(row.get("description", ""))
        if title:
            job_text += title + ". "
        if desc and desc != "nan":
            job_text += desc[:500]  # Limiter pour la vitesse

        if use_semantic and cv_text and job_text:
            # Matching hybride
            match_result = hybrid_match(
                cv_skills, job_skills, cv_text, job_text
            )
            score = match_result["final_score"]
            common = match_result["common_skills"]
            missing = match_result["missing_skills"]
            extra = match_result["extra_skills"]
            skill_score = match_result["skill_score"]
            semantic_score = match_result["semantic_score"]
        else:
            # Matching classique
            match_result = match_cv_job(cv_skills, job_skills)
            score = match_result["score"]
            common = match_result["common_skills"]
            missing = match_result["missing_skills"]
            extra = match_result["extra_skills"]
            skill_score = score
            semantic_score = 0.0

        job_info = {
            "job_id": str(row.get("job_id", idx)),
            "title": str(row.get("title", "Inconnu")),
            "company": str(row.get("company_name", "Inconnue")),
            "location": str(row.get("location", "")),
            "score": round(score, 2),
            "skill_score": round(skill_score, 2),
            "semantic_score": round(semantic_score, 2),
            "common_skills": common,
            "missing_skills": missing,
            "extra_skills": extra,
            "job_skills_count": len(job_skills),
            "cv_skills_count": len(cv_skills),
            "common_count": len(common),
        }
        recommendations.append(job_info)

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:top_n]