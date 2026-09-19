# recree_final.py
import os

# Contenu des fichiers (chaînes brutes avec triple guillemets)
files = {}

# 1. skills_dictionary.py (exactement le code que tu as partagé)
files["skills_dictionary.py"] = '''"""
skills_dictionary.py

Dictionnaire central des compétences utilisé dans JobPulse AI.

Ce fichier est partagé par tous les modules IA.

Modules utilisant ce dictionnaire :
- Extract Skills
- Resume Parser
- Skill Gap
- Recommendation System
- Job Matching
"""

from typing import Dict, List


# ==========================================================
# Dictionnaire des compétences
# ==========================================================

SKILLS_BY_CATEGORY: Dict[str, List[str]] = {

    # -----------------------------------------
    # Programming Languages
    # -----------------------------------------
    "programming_languages": [
        "python",
        "r",
        "sql",
        "java",
        "javascript",
        "typescript",
        "scala",
        "c",
        "c++",
        "c#",
        "go",
        "matlab",
        "bash"
    ],

    # -----------------------------------------
    # Data Science & AI
    # -----------------------------------------
    "data_science_ai": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "natural language processing",
        "nlp",
        "computer vision",
        "reinforcement learning",
        "data mining",
        "statistics",
        "probability",
        "predictive modeling",
        "time series",
        "forecasting",
        "feature engineering",
        "feature selection",
        "classification",
        "regression",
        "clustering",
        "anomaly detection"
    ],

    # -----------------------------------------
    # Python Libraries
    # -----------------------------------------
    "python_libraries": [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "seaborn",
        "plotly",
        "scikit-learn",
        "tensorflow",
        "keras",
        "pytorch",
        "xgboost",
        "lightgbm",
        "catboost",
        "opencv",
        "spacy",
        "nltk",
        "gensim",
        "transformers",
        "sentence-transformers",
        "hugging face",
        "langchain",
        "faiss"
    ],

    # -----------------------------------------
    # Business Intelligence
    # -----------------------------------------
    "business_intelligence": [
        "power bi",
        "tableau",
        "qlik",
        "looker",
        "excel",
        "google data studio"
    ],

    # -----------------------------------------
    # Data Engineering
    # -----------------------------------------
    "data_engineering": [
        "spark",
        "pyspark",
        "hadoop",
        "hive",
        "kafka",
        "airflow",
        "dbt",
        "etl",
        "elt",
        "data warehouse",
        "lakehouse",
        "databricks"
    ],

    # -----------------------------------------
    # Databases
    # -----------------------------------------
    "databases": [
        "postgresql",
        "mysql",
        "sql server",
        "oracle",
        "sqlite",
        "mongodb",
        "redis",
        "snowflake",
        "bigquery",
        "cassandra"
    ],

    # -----------------------------------------
    # Cloud & DevOps
    # -----------------------------------------
    "cloud_devops": [
        "aws",
        "azure",
        "google cloud",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "jenkins",
        "github actions",
        "git",
        "github",
        "linux"
    ],

    # -----------------------------------------
    # Web Development
    # -----------------------------------------
    "web_frameworks": [
        "fastapi",
        "flask",
        "django",
        "streamlit",
        "gradio",
        "rest api",
        "graphql"
    ],

    # -----------------------------------------
    # Data Visualization
    # -----------------------------------------
    "visualization": [
        "plotly",
        "matplotlib",
        "seaborn",
        "dash",
        "power bi",
        "tableau"
    ],

    # -----------------------------------------
    # Soft Skills
    # -----------------------------------------
    "soft_skills": [
        "communication",
        "problem solving",
        "critical thinking",
        "teamwork",
        "leadership",
        "project management",
        "adaptability",
        "time management"
    ]
}


# ==========================================================
# Liste unique de toutes les compétences
# ==========================================================

SKILLS = sorted({
    skill.lower().strip()
    for category in SKILLS_BY_CATEGORY.values()
    for skill in category
})


# ==========================================================
# Retourner toutes les compétences
# ==========================================================

def get_all_skills() -> List[str]:
    """
    Retourne toutes les compétences disponibles.
    """
    return SKILLS


# ==========================================================
# Retourner toutes les catégories
# ==========================================================

def get_all_categories() -> List[str]:
    """
    Retourne la liste des catégories.
    """
    return list(SKILLS_BY_CATEGORY.keys())


# ==========================================================
# Retourner les compétences d'une catégorie
# ==========================================================

def get_skills_by_category(category: str) -> List[str]:
    """
    Retourne toutes les compétences d'une catégorie.
    """
    return SKILLS_BY_CATEGORY.get(category.lower(), [])


# ==========================================================
# Trouver la catégorie d'une compétence
# ==========================================================

def get_skill_category(skill: str) -> str:
    """
    Retourne la catégorie d'une compétence.
    """
    skill = skill.lower().strip()

    for category, skills in SKILLS_BY_CATEGORY.items():
        if skill in skills:
            return category

    return "other"


# ==========================================================
# Vérifier si une compétence existe
# ==========================================================

def skill_exists(skill: str) -> bool:
    """
    Vérifie si une compétence existe dans le dictionnaire.
    """
    return skill.lower().strip() in SKILLS


# ==========================================================
# Rechercher des compétences contenant un mot
# ==========================================================

def search_skills(keyword: str) -> List[str]:
    """
    Recherche des compétences contenant un mot.
    Exemple :
        search_skills("python")
    """
    keyword = keyword.lower().strip()

    return sorted(
        [
            skill
            for skill in SKILLS
            if keyword in skill
        ]
    )


# ==========================================================
# Statistiques
# ==========================================================

def get_statistics() -> dict:
    """
    Retourne quelques statistiques sur le dictionnaire.
    """

    return {
        "categories": len(SKILLS_BY_CATEGORY),
        "skills": len(SKILLS),
        "skills_per_category": {
            category: len(skills)
            for category, skills in SKILLS_BY_CATEGORY.items()
        }
    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("JobPulse AI - Skills Dictionary")
    print("=" * 50)

    print("\\nNombre total de compétences :", len(SKILLS))
    print("\\nCatégories :", get_all_categories())

    print("\\nCatégorie de Docker :")
    print(get_skill_category("docker"))

    print("\\nRecherche 'python' :")
    print(search_skills("python"))

    print("\\nStatistiques :")
    print(get_statistics())
'''

# 2. text_cleaner.py
files["text_cleaner.py"] = '''# ml/nlp/text_cleaner.py
import re
import unicodedata

def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[\\r\\n\\t]+', ' ', text)
    text = re.sub(r'[^a-z0-9\\s]', ' ', text)
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

def tokenize_words(text: str) -> list:
    return text.split() if text else []
'''

# 3. extract_skills.py
files["extract_skills.py"] = '''# ml/nlp/extract_skills.py
import re
from .skills_dictionary import SKILLS, get_skill_category
from .text_cleaner import clean_text

def extract_skills(text: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"skills": [], "categorized": {}}
    sorted_skills = sorted(SKILLS, key=len, reverse=True)
    found = set()
    remaining_text = cleaned
    for skill in sorted_skills:
        pattern = r'\\b' + re.escape(skill) + r'\\b'
        if re.search(pattern, remaining_text):
            found.add(skill)
            remaining_text = re.sub(pattern, ' ' * len(skill), remaining_text)
    skills_list = sorted(list(found))
    categorized = {}
    for skill in skills_list:
        cat = get_skill_category(skill)
        categorized.setdefault(cat, []).append(skill)
    return {"skills": skills_list, "categorized": categorized}

def extract_skills_from_list(texts: list) -> list:
    return [extract_skills(t) for t in texts]
'''

# 4. resume_parser.py
files["resume_parser.py"] = '''# ml/nlp/resume_parser.py
import pdfplumber
from .text_cleaner import clean_text

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\\n"
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'extraction du PDF : {e}")
    return text.strip()

def extract_name(text: str) -> str:
    lines = text.splitlines()
    for line in lines:
        if line.strip():
            return line.strip()
    return "Inconnu"

def extract_sections(text: str) -> dict:
    return {"experience": "", "education": "", "skills": "", "other": text}

def parse_resume(pdf_path: str) -> dict:
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned = clean_text(raw_text)
    name = extract_name(raw_text)
    sections = extract_sections(raw_text)
    return {
        "name": name,
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "sections": sections
    }
'''

# 5. resume_analyzer.py
files["resume_analyzer.py"] = '''# ml/nlp/resume_analyzer.py
from .extract_skills import extract_skills
from .resume_parser import parse_resume

def analyze_resume(pdf_path: str) -> dict:
    parsed = parse_resume(pdf_path)
    skills_result = extract_skills(parsed["cleaned_text"])
    skills = skills_result["skills"]
    categorized = skills_result["categorized"]
    domains = [cat for cat, sk in categorized.items() if len(sk) >= 2]
    seniority = "junior"
    return {
        "name": parsed["name"],
        "skills": skills,
        "categorized_skills": categorized,
        "domains": domains,
        "seniority": seniority,
        "sections": parsed["sections"]
    }
'''

# 6. job_matcher.py
files["job_matcher.py"] = '''# ml/nlp/job_matcher.py
from .extract_skills import extract_skills

def match_cv_job(cv_skills: list, job_skills: list) -> dict:
    cv_set = set(s.lower().strip() for s in cv_skills)
    job_set = set(s.lower().strip() for s in job_skills)
    common = cv_set & job_set
    missing = job_set - cv_set
    extra = cv_set - job_set
    score = len(common) / len(job_set) if job_set else 0.0
    score_percent = round(score * 100, 2)
    return {
        "score": score_percent,
        "common_skills": sorted(list(common)),
        "missing_skills": sorted(list(missing)),
        "extra_skills": sorted(list(extra)),
        "cv_skills_count": len(cv_set),
        "job_skills_count": len(job_set),
        "common_count": len(common)
    }

def match_cv_job_from_texts(cv_text: str, job_text: str) -> dict:
    cv_result = extract_skills(cv_text)
    job_result = extract_skills(job_text)
    return match_cv_job(cv_result["skills"], job_result["skills"])

def match_cv_job_from_profile(profile: dict, job_text: str) -> dict:
    cv_skills = profile.get("skills", [])
    job_result = extract_skills(job_text)
    return match_cv_job(cv_skills, job_result["skills"])
'''

# 7. skill_gap.py
files["skill_gap.py"] = '''# ml/nlp/skill_gap.py
from .skills_dictionary import get_skill_category
from .extract_skills import extract_skills

def compute_skill_gap(profile: dict, job_skills: list) -> dict:
    cv_skills = set(s.lower().strip() for s in profile.get("skills", []))
    job_set = set(s.lower().strip() for s in job_skills)
    missing = job_set - cv_skills
    gap_by_category = {}
    for skill in missing:
        cat = get_skill_category(skill)
        gap_by_category.setdefault(cat, []).append(skill)
    for cat in gap_by_category:
        gap_by_category[cat].sort()
    return {
        "gap_by_category": gap_by_category,
        "total_missing": len(missing),
        "missing_skills": sorted(list(missing)),
        "summary": f"Il manque {len(missing)} compétence(s) pour ce poste."
    }

def compute_skill_gap_from_texts(profile: dict, job_text: str) -> dict:
    job_result = extract_skills(job_text)
    return compute_skill_gap(profile, job_result["skills"])
'''

# 8. recommender.py
files["recommender.py"] = '''# ml/nlp/recommender.py
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
'''

# Écrire chaque fichier en mode binaire avec encodage utf-8
target_dir = "ml/nlp"
os.makedirs(target_dir, exist_ok=True)

for filename, content in files.items():
    filepath = os.path.join(target_dir, filename)
    # Écriture en binaire pour éviter tout ajout de BOM ou conversion de fin de ligne
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf-8'))
    print(f"✅ Fichier créé : {filepath}")

print("\n✅ Tous les fichiers du module NLP ont été recréés avec un encodage utf-8 strict.")