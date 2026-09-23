# backend/app/services/auth_service.py
"""
Service d'authentification (JWT + bcrypt pur).
NOTE: bcrypt limite les mots de passe à 72 bytes en UTF-8.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from app.database import User

SECRET_KEY = os.getenv("JWT_SECRET", "jobpulseai-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


# ============================================================
# HASH DE MOT DE PASSE (bcrypt pur, sans passlib)
# ============================================================
def _truncate_password(password: str) -> bytes:
    """Tronque le mot de passe à 72 bytes max (limite bcrypt)."""
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    else:
        password_bytes = password
    return password_bytes[:72]


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    password_bytes = _truncate_password(password)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    password_bytes = _truncate_password(plain)
    try:
        return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))
    except Exception as e:
        print(f"⚠️ Erreur verify_password : {e}")
        return False


# ============================================================
# JWT TOKENS
# ============================================================
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================
# INSCRIPTION & CONNEXION
# ============================================================
def register_user(db: Session, email: str, password: str, full_name: str = "") -> User:
    """Inscrit un nouvel utilisateur."""
    # Vérifier l'existence
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Cet email est déjà utilisé")

    # Créer l'utilisateur
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authentifie un utilisateur."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user