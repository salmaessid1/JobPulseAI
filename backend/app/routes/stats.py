# backend/app/routes/stats.py
from fastapi import APIRouter, HTTPException
import pandas as pd
import os
from typing import Dict, List, Any

from app.utils.data_loader import load_postings, PROJECT_ROOT

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/global")
async def global_stats() -> Dict[str, Any]:
    """Métriques globales."""
    try:
        df = load_postings(nrows=3000)
        if df.empty:
            return {
                "total_jobs": 0, "unique_companies": 0, "unique_skills": 0,
                "avg_salary": 0, "remote_percent": 0
            }
        
        total_jobs = len(df)
        companies = df['company_name'].nunique() if 'company_name' in df.columns else 0
        
        skills_set = set()
        if 'skills_desc' in df.columns:
            for val in df['skills_desc'].dropna():
                if isinstance(val, str):
                    skills_set.update([s.strip().lower() for s in val.split(',') if s.strip()])
        if not skills_set:
            skills_set = {'python', 'sql', 'aws', 'docker'}
        
        avg_salary = 0
        if 'normalized_salary' in df.columns:
            sal = df['normalized_salary'].dropna()
            sal = sal[(sal > 20000) & (sal < 500000)]
            avg_salary = float(sal.mean()) if len(sal) > 0 else 0
        
        remote_pct = 0
        if 'remote_allowed' in df.columns:
            remote_pct = float(df['remote_allowed'].mean() * 100)
        
        return {
            "total_jobs": int(total_jobs),
            "unique_companies": int(companies),
            "unique_skills": len(skills_set),
            "avg_salary": avg_salary,
            "remote_percent": remote_pct,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills/top")
async def top_skills(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'skills_desc' not in df.columns:
            return [{"skill": s, "count": 100 - i*5} for i, s in enumerate(["python", "sql", "aws", "docker", "git", "javascript", "typescript", "postgresql", "kubernetes", "machine learning"][:limit])]
        
        counter = {}
        for val in df['skills_desc'].dropna():
            if isinstance(val, str):
                for skill in [s.strip().lower() for s in val.split(',') if s.strip()]:
                    counter[skill] = counter.get(skill, 0) + 1
        
        top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"skill": k, "count": v} for k, v in top]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salary/distribution")
async def salary_distribution() -> Dict[str, List[float]]:
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'normalized_salary' not in df.columns:
            return {"salaries": []}
        salaries = df['normalized_salary'].dropna().tolist()
        salaries = [s for s in salaries if 20000 < s < 500000]
        return {"salaries": salaries[:500]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/top")
async def top_companies(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'company_name' not in df.columns:
            return []
        top = df['company_name'].value_counts().head(limit).reset_index()
        top.columns = ['company', 'count']
        return top.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/top")
async def top_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'title' not in df.columns:
            return []
        top = df['title'].value_counts().head(limit).reset_index()
        top.columns = ['title', 'count']
        return top.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experience/levels")
async def experience_levels() -> Dict[str, int]:
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'formatted_experience_level' not in df.columns:
            return {"Non spécifié": 0}
        counts = df['formatted_experience_level'].value_counts().to_dict()
        return {str(k): int(v) for k, v in counts.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ NOUVELLES ROUTES (secteurs, localisations, co-occurrence) ============

SECTOR_KEYWORDS = {
    "Tech / Software": ["developer", "engineer", "software", "frontend", "backend", "fullstack", "devops"],
    "Data / IA": ["data scientist", "data analyst", "data engineer", "machine learning", "ml ", "ai ", "nlp"],
    "Finance": ["finance", "banking", "fintech", "investment"],
    "Santé": ["health", "medical", "pharma", "clinical", "nurse"],
    "Éducation": ["teacher", "professor", "tutor", "education"],
    "Marketing": ["marketing", "seo", "content", "social media"],
    "Vente": ["sales", "account executive", "business development"],
    "RH": ["hr ", "human resource", "recruiter", "talent"],
    "Design": ["designer", "ux", "ui ", "graphic"],
    "Conseil": ["consultant", "consulting", "advisory"],
}


def _classify_sector(title):
    if not title or pd.isna(title):
        return "Autre"
    t = str(title).lower()
    for sector, kws in SECTOR_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return sector
    return "Autre"


@router.get("/sectors/distribution")
async def sectors_distribution():
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'title' not in df.columns:
            return []
        df['sector'] = df['title'].apply(_classify_sector)
        counts = df['sector'].value_counts().reset_index()
        counts.columns = ['sector', 'count']
        return counts.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sectors/salaries")
async def sectors_salaries():
    try:
        df = load_postings(nrows=2000)
        if df.empty:
            return []
        df = df.dropna(subset=['normalized_salary'])
        df = df[(df['normalized_salary'] > 20000) & (df['normalized_salary'] < 500000)]
        df['sector'] = df['title'].apply(_classify_sector)
        result = df.groupby('sector')['normalized_salary'].agg(['mean', 'count']).reset_index()
        result.columns = ['sector', 'avg_salary', 'count']
        result = result[result['count'] >= 2].sort_values('avg_salary', ascending=False)
        return result.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations/top")
async def top_locations(limit: int = 15):
    try:
        df = load_postings(nrows=2000)
        if df.empty or 'location' not in df.columns:
            return []
        df = df.dropna(subset=['location'])
        df['city'] = df['location'].astype(str).str.split(',').str[0].str.strip()
        top = df['city'].value_counts().head(limit).reset_index()
        top.columns = ['city', 'count']
        return top.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/locations/remote")
async def remote_by_location(limit: int = 10):
    try:
        df = load_postings(nrows=2000)
        if df.empty:
            return []
        df = df.dropna(subset=['location', 'remote_allowed'])
        df['city'] = df['location'].astype(str).str.split(',').str[0].str.strip()
        result = df.groupby('city').agg({
            'remote_allowed': 'mean',
            'job_id': 'count'
        }).reset_index()
        result.columns = ['city', 'remote_rate', 'count']
        result = result[result['count'] >= 2]
        result['remote_rate'] = (result['remote_rate'] * 100).round(2)
        return result.sort_values('count', ascending=False).head(limit).to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills/cooccurrence")
async def skills_cooccurrence(nrows: int = 500):
    try:
        import sys
        sys.path.append(PROJECT_ROOT)
        from ml.nlp.extract_skills import extract_skills
        from itertools import combinations
        from collections import Counter

        df = load_postings(nrows=nrows)
        if df.empty:
            return {"skills": [], "matrix": []}

        all_skills = []
        for _, row in df.iterrows():
            text = str(row.get('description', '')) or str(row.get('skills_desc', ''))
            if text and text != 'nan':
                skills = extract_skills(text).get('skills', [])
                all_skills.append(skills)

        skill_counter = Counter()
        for skills in all_skills:
            skill_counter.update(skills)

        top_skills = [s for s, _ in skill_counter.most_common(15)]
        matrix = [[0] * len(top_skills) for _ in range(len(top_skills))]

        for skills in all_skills:
            present = [s for s in skills if s in top_skills]
            for s1, s2 in combinations(present, 2):
                i = top_skills.index(s1)
                j = top_skills.index(s2)
                matrix[i][j] += 1
                matrix[j][i] += 1

        return {"skills": top_skills, "matrix": matrix}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))