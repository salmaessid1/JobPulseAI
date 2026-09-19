# backend/app/services/matching_service.py
import os
import sys
from typing import Dict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

# Import direct
from ml.nlp.job_matcher import match_cv_job_from_texts


def match_cv_job(cv_text: str, job_text: str) -> Dict:
    """
    Compare un CV (texte) avec une description de poste.
    """
    result = match_cv_job_from_texts(cv_text, job_text)
    return result