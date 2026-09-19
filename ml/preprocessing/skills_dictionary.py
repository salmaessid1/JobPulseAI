"""
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

    print("\nNombre total de compétences :", len(SKILLS))
    print("\nCatégories :", get_all_categories())

    print("\nCatégorie de Docker :")
    print(get_skill_category("docker"))

    print("\nRecherche 'python' :")
    print(search_skills("python"))

    print("\nStatistiques :")
    print(get_statistics())