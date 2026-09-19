# backend/app/services/skill_gap_service.py
# Service pour le skill gap

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from typing import Dict
from ml.nlp.skill_gap import compute_skill_gap_from_texts
from ml.nlp.resume_analyzer import analyze_resume

def skill_gap_from_cv_profile(profile: Dict, job_text: str) -> Dict:
    """
    Calcule le gap entre un profil CV et une offre.
    """
    return compute_skill_gap_from_texts(profile, job_text)