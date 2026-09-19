# backend/app/services/cooccurrence_service.py
import os
import sys
import pandas as pd
from itertools import combinations
from typing import List, Dict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

from ml.nlp.extract_skills import extract_skills


def compute_cooccurrence(nrows: int = 500) -> Dict:
    """Calcule la matrice de co-occurrence des compétences."""
    path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")
    if not os.path.exists(path):
        path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
    
    if not os.path.exists(path):
        return {"skills": [], "matrix": []}
    
    df = pd.read_csv(path, nrows=nrows, low_memory=False)
    
    # Extraire les compétences de chaque offre
    all_skills = []
    for _, row in df.iterrows():
        text = str(row.get('description', '')) or str(row.get('skills_desc', ''))
        if text and text != 'nan':
            skills = extract_skills(text).get('skills', [])
            all_skills.append(skills)
    
    # Compter les occurrences
    from collections import Counter
    skill_counter = Counter()
    for skills in all_skills:
        skill_counter.update(skills)
    
    # Top 15 compétences
    top_skills = [s for s, _ in skill_counter.most_common(15)]
    
    # Matrice de co-occurrence
    matrix = [[0] * len(top_skills) for _ in range(len(top_skills))]
    for skills in all_skills:
        present = [s for s in skills if s in top_skills]
        for s1, s2 in combinations(present, 2):
            i = top_skills.index(s1)
            j = top_skills.index(s2)
            matrix[i][j] += 1
            matrix[j][i] += 1
    
    return {
        "skills": top_skills,
        "matrix": matrix,
    }