# backend/app/routes/jobs.py
# Routes pour les offres d'emploi

from fastapi import APIRouter
from app.services.recommendation_service import load_jobs_data

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/")
async def get_jobs(limit: int = 100):
    """
    Retourne la liste des offres (échantillon).
    """
    df = load_jobs_data()
    if df.empty:
        return []
    return df.head(limit).to_dict(orient="records")