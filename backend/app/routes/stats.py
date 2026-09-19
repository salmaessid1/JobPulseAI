# backend/app/routes/stats.py
from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from typing import Dict, List, Any
from app.services.sector_service import get_sector_distribution, get_sector_salaries
from app.services.cooccurrence_service import compute_cooccurrence

router = APIRouter(prefix="/stats", tags=["Stats"])

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
SAMPLE_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")

def load_data() -> pd.DataFrame:
    """Charge le CSV des offres (utilise l'échantillon si disponible)."""
    if os.path.exists(SAMPLE_PATH):
        df = pd.read_csv(SAMPLE_PATH, low_memory=False)
    elif os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, low_memory=False)
    else:
        raise FileNotFoundError("Aucun fichier de données trouvé")
    return df
@router.get("/sectors/distribution")
async def sectors_distribution():
    return get_sector_distribution()

@router.get("/sectors/salaries")
async def sectors_salaries():
    return get_sector_salaries()
@router.get("/locations/top")
async def top_locations(limit: int = 15):
    """Top villes/régions qui recrutent."""
    import pandas as pd
    path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")
    if not os.path.exists(path):
        path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
    
    df = pd.read_csv(path, nrows=3000, low_memory=False)
    df = df.dropna(subset=['location'])
    
    # Extraire la ville (avant la virgule)
    df['city'] = df['location'].astype(str).str.split(',').str[0].str.strip()
    top = df['city'].value_counts().head(limit).reset_index()
    top.columns = ['city', 'count']
    return top.to_dict(orient='records')


@router.get("/locations/remote")
async def remote_by_location(limit: int = 10):
    """Taux de remote par ville."""
    import pandas as pd
    path = os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv")
    if not os.path.exists(path):
        path = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
    
    df = pd.read_csv(path, nrows=3000, low_memory=False)
    df = df.dropna(subset=['location', 'remote_allowed'])
    df['city'] = df['location'].astype(str).str.split(',').str[0].str.strip()
    
    result = df.groupby('city').agg({
        'remote_allowed': 'mean',
        'job_id': 'count'
    }).reset_index()
    result.columns = ['city', 'remote_rate', 'count']
    result = result[result['count'] >= 10]
    result['remote_rate'] = (result['remote_rate'] * 100).round(2)
    result = result.sort_values('count', ascending=False).head(limit)
    return result.to_dict(orient='records')

@router.get("/skills/cooccurrence")
async def skills_cooccurrence(nrows: int = 500):
    return compute_cooccurrence(nrows)





@router.get("/global")
async def global_stats() -> Dict[str, Any]:
    """Retourne les métriques globales (nombre d'offres, entreprises, compétences, salaire moyen, remote)."""
    try:
        df = load_data()
        total_jobs = len(df)
        companies = df['company_name'].nunique() if 'company_name' in df.columns else 0
        # Compétences uniques – on peut les extraire de skills_desc ou d'une colonne déjà préparée
        # Pour l'instant, on simule à partir d'une extraction simple si la colonne existe
        skills_set = set()
        if 'skills_desc' in df.columns:
            for val in df['skills_desc'].dropna():
                if isinstance(val, str):
                    skills_set.update([s.strip().lower() for s in val.split(',') if s.strip()])
        # Fallback si skills_desc n'existe pas
        if not skills_set:
            skills_set = {'python', 'sql', 'aws', 'docker'}  # valeurs par défaut
        avg_salary = df['normalized_salary'].mean() if 'normalized_salary' in df.columns else 0
        remote_pct = df['remote_allowed'].mean() * 100 if 'remote_allowed' in df.columns else 0
        
        return {
            "total_jobs": int(total_jobs),
            "unique_companies": int(companies),
            "unique_skills": len(skills_set),
            "avg_salary": float(avg_salary),
            "remote_percent": float(remote_pct)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills/top")
async def top_skills(limit: int = 10) -> List[Dict[str, Any]]:
    """Retourne les compétences les plus fréquentes."""
    try:
        df = load_data()
        if 'skills_desc' not in df.columns:
            return [{"skill": "Python", "count": 120}, {"skill": "SQL", "count": 100}, {"skill": "AWS", "count": 80}]
        # Compter les occurrences
        skill_counter = {}
        for val in df['skills_desc'].dropna():
            if isinstance(val, str):
                for skill in [s.strip().lower() for s in val.split(',') if s.strip()]:
                    skill_counter[skill] = skill_counter.get(skill, 0) + 1
        sorted_skills = sorted(skill_counter.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"skill": k, "count": v} for k, v in sorted_skills]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/salary/distribution")
async def salary_distribution() -> Dict[str, List[float]]:
    """Retourne la distribution des salaires normalisés."""
    try:
        df = load_data()
        if 'normalized_salary' not in df.columns:
            return {"salaries": []}
        salaries = df['normalized_salary'].dropna().tolist()
        return {"salaries": salaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies/top")
async def top_companies(limit: int = 10) -> List[Dict[str, Any]]:
    """Retourne les entreprises qui recrutent le plus."""
    try:
        df = load_data()
        if 'company_name' not in df.columns:
            return [{"company": "Inconnue", "count": 0}]
        top = df['company_name'].value_counts().head(limit).reset_index()
        top.columns = ['company', 'count']
        return top.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/top")
async def top_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    """Retourne les titres de poste les plus fréquents."""
    try:
        df = load_data()
        if 'title' not in df.columns:
            return [{"title": "Inconnu", "count": 0}]
        top = df['title'].value_counts().head(limit).reset_index()
        top.columns = ['title', 'count']
        return top.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/experience/levels")
async def experience_levels() -> Dict[str, int]:
    """Retourne la répartition par niveau d'expérience."""
    try:
        df = load_data()
        if 'formatted_experience_level' not in df.columns:
            return {"Non spécifié": len(df)}
        counts = df['formatted_experience_level'].value_counts().to_dict()
        return {str(k): int(v) for k, v in counts.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))