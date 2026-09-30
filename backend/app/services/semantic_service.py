# backend/app/services/semantic_service.py
"""
Service FastAPI pour le matching sémantique.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
sys.path.append(PROJECT_ROOT)

from ml.nlp.semantic_matcher import (
    semantic_similarity,
    semantic_similarity_batch,
    hybrid_match,
)


def compute_semantic_match(cv_text: str, job_text: str) -> dict:
    """Retourne uniquement le score sémantique."""
    score = semantic_similarity(cv_text, job_text)
    return {
        "semantic_score": score,
        "model": "all-MiniLM-L6-v2",
    }


def compute_hybrid_match(
    cv_skills: list,
    job_skills: list,
    cv_text: str,
    job_text: str,
) -> dict:
    """Retourne le matching hybride complet."""
    return hybrid_match(cv_skills, job_skills, cv_text, job_text)