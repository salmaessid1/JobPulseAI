# backend/app/database.py
"""
Base de données SQLite pour l'historique des analyses JobPulseAI.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./jobpulseai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisHistory(Base):
    """Historique de toutes les analyses."""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), index=True, default="Anonyme")
    analysis_type = Column(String(50), index=True)  # cv, matching, skill_gap, salary
    input_summary = Column(Text)  # Résumé court de l'entrée
    result_data = Column(JSON)     # Résultat complet en JSON
    score = Column(Float, nullable=True)  # Score principal (si applicable)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class JobCache(Base):
    """Cache des offres d'emploi pour éviter les rechargements CSV."""
    __tablename__ = "jobs_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    skills = Column(JSON)
    salary_normalized = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Crée toutes les tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée : jobpulseai.db")


def get_db():
    """Dependency pour FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()


class Conversation(Base):
    """Conversation du chatbot."""
    __tablename__ = "conversations"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(100), default="default", index=True)
    title = Column(String(200), default="Nouvelle conversation")
    pinned = Column(Integer, default=0)  # 0 ou 1
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    """Message d'une conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String(50), index=True)
    role = Column(String(20))  # "user" ou "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    """Utilisateur de l'application."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    full_name = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)