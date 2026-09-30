# backend/app/routes/semantic.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.semantic_matching_service import semantic_match

router = APIRouter(prefix="/semantic", tags=["Semantic"])


class MatchRequest(BaseModel):
    cv_text: str
    job_text: str


@router.post("/match")
async def match(request: MatchRequest):
    try:
        return semantic_match(request.cv_text, request.job_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Erreur semantic_match : {e}")
        raise HTTPException(status_code=500, detail=str(e))