# backend/app/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import (
    register_user, authenticate_user, create_access_token, decode_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    token: str


@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur."""
    try:
        if len(data.password) < 6:
            raise HTTPException(status_code=400, detail="Mot de passe trop court (min. 6)")
        user = register_user(db, data.email, data.password, data.full_name)
        token = create_access_token({"sub": str(user.id), "email": user.email})
        return AuthResponse(
            user_id=user.id, email=user.email,
            full_name=user.full_name or "", token=token
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Connexion."""
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return AuthResponse(
        user_id=user.id, email=user.email,
        full_name=user.full_name or "", token=token
    )


@router.get("/me")
async def get_me(token: str, db: Session = Depends(get_db)):
    """Récupère le profil actuel."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    from app.database import User
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"user_id": user.id, "email": user.email, "full_name": user.full_name}