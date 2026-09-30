from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.job_classifier_service import classify_job

router = APIRouter(prefix="/classify", tags=["Classification"])

class ClassifyRequest(BaseModel):
    text: str

@router.post("/job")
async def classify(request: ClassifyRequest):
    try:
        return classify_job(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))