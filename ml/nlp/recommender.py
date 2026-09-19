# ml/nlp/recommender.py
import pandas as pd
from typing import List, Dict, Optional
from .extract_skills import extract_skills
from .job_matcher import match_cv_job

def load_jobs(file_path: str, sample_size: Optional[int] = None) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=42)
    return df

def extract_job_skills_from_row(row: pd.Series) -> List[str]:
    text = row.get("description", "")
    if pd.isna(text) or not text.strip():
        text = row.get("skills_desc", "")
    if pd.isna(text) or not text.strip():
        return []
    result = extract_skills(text)
    return result["skills"]

def recommend_jobs(profile: Dict, jobs_df: pd.DataFrame, top_n: int = 10) -> List[Dict]:
    cv_skills = profile.get("skills", [])
    if not cv_skills:
        return []
    recommendations = []
    for idx, row in jobs_df.iterrows():
        job_skills = extract_job_skills_from_row(row)
        if not job_skills:
            continue
        match_result = match_cv_job(cv_skills, job_skills)
        job_info = {
            "job_id": row.get("job_id", idx),
            "title": row.get("title", "Inconnu"),
            "company": row.get("company_name", "Inconnue"),
            "location": row.get("location", ""),
            "score": match_result["score"],
            "common_skills": match_result["common_skills"],
            "missing_skills": match_result["missing_skills"],
            "extra_skills": match_result["extra_skills"],
            "job_skills_count": match_result["job_skills_count"],
            "cv_skills_count": match_result["cv_skills_count"],
            "common_count": match_result["common_count"]
        }
        recommendations.append(job_info)
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:top_n]
