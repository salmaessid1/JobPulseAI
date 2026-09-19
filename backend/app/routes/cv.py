# backend/app/routes/cv.py
# Routes pour l'analyse de CV

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.cv_service import analyze_cv_file
from app.schemas import CVUploadResponse

router = APIRouter(prefix="/cv", tags=["CV"])

@router.post("/upload", response_model=CVUploadResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload un CV (PDF) et retourne le profil structuré.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les PDF sont acceptés")
    
    try:
        content = await file.read()
        profile = analyze_cv_file(content, file.filename)
        return CVUploadResponse(filename=file.filename, profile=profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))