# backend/app/routes/skill_gap.py
# Route pour le skill gap

from fastapi import APIRouter, HTTPException
from app.schemas import SkillGapRequest, SkillGapResponse
from app.services.skill_gap_service import skill_gap_from_cv_profile

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap"])

@router.post("/", response_model=SkillGapResponse)
async def compute_skill_gap(request: SkillGapRequest):
    """
    Calcule les compétences manquantes entre un profil CV et une offre.
    """
    try:
        result = skill_gap_from_cv_profile(request.profile, request.job_text)
        return SkillGapResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))