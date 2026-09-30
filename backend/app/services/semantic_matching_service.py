# backend/app/services/semantic_matching_service.py
import os
import sys
from typing import Dict

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.append(PROJECT_ROOT)

from ml.nlp.semantic_matcher import hybrid_match, semantic_similarity
from ml.nlp.extract_skills import extract_skills


def semantic_match(cv_text: str, job_text: str) -> Dict:
    """
    Effectue un matching sémantique complet entre un CV et une offre.
    """
    if not cv_text or not job_text:
        raise ValueError("cv_text et job_text sont requis")

    # Extraire les compétences des deux textes
    cv_skills_result = extract_skills(cv_text)
    job_skills_result = extract_skills(job_text)

    cv_skills = cv_skills_result.get("skills", [])
    job_skills = job_skills_result.get("skills", [])

    # Matching hybride
    result = hybrid_match(cv_skills, job_skills, cv_text, job_text)

    # Ajouter les infos textuelles
    result["cv_skills"] = cv_skills
    result["job_skills"] = job_skills

    return result