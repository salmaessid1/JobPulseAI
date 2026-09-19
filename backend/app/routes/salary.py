# backend/app/routes/salary.py
# Route pour la prédiction de salaire

from fastapi import APIRouter, HTTPException
from app.schemas import SalaryRequest, SalaryResponse
from app.services.salary_service import predict_salary

router = APIRouter(prefix="/salary", tags=["Salary"])

@router.post("/predict", response_model=SalaryResponse)
async def predict(request: SalaryRequest):
    """
    Prédit le salaire à partir des caractéristiques du poste.
    """
    try:
        result = predict_salary(request.dict())
        return SalaryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))