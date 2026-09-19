# backend/app/routes/history.py
"""Routes pour l'historique des analyses."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db, AnalysisHistory

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/", response_model=List[Dict])
async def get_history(limit: int = 50, analysis_type: str = None, db: Session = Depends(get_db)):
    """Retourne l'historique des analyses."""
    query = db.query(AnalysisHistory).order_by(AnalysisHistory.created_at.desc())
    if analysis_type:
        query = query.filter(AnalysisHistory.analysis_type == analysis_type)
    items = query.limit(limit).all()
    return [
        {
            "id": item.id,
            "user_name": item.user_name,
            "analysis_type": item.analysis_type,
            "input_summary": item.input_summary,
            "score": item.score,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in items
    ]


@router.get("/stats")
async def get_history_stats(db: Session = Depends(get_db)):
    """Statistiques sur l'historique."""
    total = db.query(AnalysisHistory).count()
    by_type = {}
    for atype in ["cv", "matching", "skill_gap", "salary"]:
        count = db.query(AnalysisHistory).filter(AnalysisHistory.analysis_type == atype).count()
        by_type[atype] = count
    return {"total": total, "by_type": by_type}


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Supprime une analyse."""
    item = db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    db.delete(item)
    db.commit()
    return {"message": "Analyse supprimée", "id": analysis_id}