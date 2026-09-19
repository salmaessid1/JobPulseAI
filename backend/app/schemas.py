# backend/app/schemas.py
# Schémas Pydantic pour les requêtes/réponses API

from pydantic import BaseModel
from typing import List, Dict, Optional

# --- CV ---
class CVUploadResponse(BaseModel):
    filename: str
    profile: Dict

# --- Matching ---
class MatchRequest(BaseModel):
    cv_text: str
    job_text: str

class MatchResponse(BaseModel):
    score: float
    common_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    cv_skills_count: int
    job_skills_count: int
    common_count: int

# --- Skill Gap ---
class SkillGapRequest(BaseModel):
    profile: Dict
    job_text: str

class SkillGapResponse(BaseModel):
    gap_by_category: Dict[str, List[str]]
    total_missing: int
    missing_skills: List[str]
    summary: str

# --- Recommendations ---
class RecommendationRequest(BaseModel):
    profile: Dict
    top_n: Optional[int] = 10

class RecommendationItem(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    score: float
    common_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]

# --- Salary Prediction ---
class SalaryRequest(BaseModel):
    title: str
    formatted_experience_level: str
    remote_allowed: int
    work_type: str
    location: str
    min_salary: float
    max_salary: float

class SalaryResponse(BaseModel):
    predicted_salary: float
    min_range: float
    max_range: float