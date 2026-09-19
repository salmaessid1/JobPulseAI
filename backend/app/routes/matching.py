# backend/app/routes/matching.py
from fastapi import APIRouter, HTTPException
from app.schemas import MatchRequest, MatchResponse
from app.services.matching_service import match_cv_job

router = APIRouter(prefix="/matching", tags=["Matching"])

@router.post("/", response_model=MatchResponse)
async def match(request: MatchRequest):
    try:
        # Timeout très court car le matching est instantané
        result = match_cv_job(request.cv_text, request.job_text)
        return MatchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))