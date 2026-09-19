# backend/app/routes/recommendations.py
from fastapi import APIRouter, HTTPException
from app.schemas import RecommendationRequest, RecommendationItem, RecommendationResponse
from app.services.recommendation_service import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/")   # <-- on retire response_model pour éviter la validation
async def recommend(request: RecommendationRequest):
    try:
        recs = get_recommendations(request.profile, request.top_n)
        # On retourne directement la liste (le dashboard s'attend à une liste)
        return recs
    except Exception as e:
        # Afficher l'erreur dans le terminal pour debug
        print(f"❌ Erreur dans /recommendations/ : {e}")
        raise HTTPException(status_code=500, detail=str(e))