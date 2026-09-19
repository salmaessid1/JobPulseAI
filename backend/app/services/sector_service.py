# backend/app/services/sector_service.py
import os
import sys
import pandas as pd
import re
from typing import Dict, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Mapping titre → secteur
SECTOR_KEYWORDS = {
    "Tech / Software": ["developer", "engineer", "software", "frontend", "backend", "fullstack", "devops", "sre"],
    "Data / IA": ["data scientist", "data analyst", "data engineer", "machine learning", "ml ", "ai ", "nlp"],
    "Finance": ["finance", "banking", "fintech", "investment", "trader", "actuary"],
    "Santé": ["health", "medical", "pharma", "clinical", "nurse", "doctor"],
    "Éducation": ["teacher", "professor", "tutor", "education", "instructor"],
    "Marketing": ["marketing", "seo", "content", "social media", "growth"],
    "Vente": ["sales", "account executive", "business development"],
    "RH": ["hr ", "human resource", "recruiter", "talent"],
    "Design": ["designer", "ux", "ui ", "graphic", "creative"],
    "Industrie": ["manufacturing", "industrial", "production", "supply chain"],
    "Conseil": ["consultant", "consulting", "advisory"],
    "Juridique": ["legal", "lawyer", "attorney", "paralegal"],
}


def classify_sector(title: str) -> str:
    """Classifie le secteur d'après le titre du poste."""
    if not title or pd.isna(title):
        return "Autre"
    t = str(title).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return sector
    return "Autre"


def get_sector_distribution(nrows: int = 2000) -> List[Dict]:
    """Retourne la distribution des offres par secteur."""
    sample_path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")
    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
    
    path = sample_path if os.path.exists(sample_path) else raw_path
    if not os.path.exists(path):
        return []
    
    df = pd.read_csv(path, nrows=nrows, low_memory=False)
    df['sector'] = df['title'].apply(classify_sector)
    
    counts = df['sector'].value_counts().reset_index()
    counts.columns = ['sector', 'count']
    return counts.to_dict(orient='records')


def get_sector_salaries(nrows: int = 2000) -> List[Dict]:
    """Retourne le salaire moyen par secteur."""
    sample_path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")
    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
    
    path = sample_path if os.path.exists(sample_path) else raw_path
    if not os.path.exists(path):
        return []
    
    df = pd.read_csv(path, nrows=nrows, low_memory=False)
    df = df.dropna(subset=['normalized_salary'])
    df = df[(df['normalized_salary'] > 20000) & (df['normalized_salary'] < 500000)]
    
    df['sector'] = df['title'].apply(classify_sector)
    
    result = df.groupby('sector')['normalized_salary'].agg(['mean', 'count']).reset_index()
    result.columns = ['sector', 'avg_salary', 'count']
    result = result[result['count'] >= 5]  # Au moins 5 offres
    result = result.sort_values('avg_salary', ascending=False)
    return result.to_dict(orient='records')