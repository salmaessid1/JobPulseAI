#Tester FastAPI
# backend/app/main.py
# Point d'entrée FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import cv, matching, skill_gap, recommendations, salary, jobs, stats
from app.database import init_db
from app.routes import history
from dotenv import load_dotenv
load_dotenv()
from app.routes import chatbot,conversations
# Après la création de l'app FastAPI

app = FastAPI(
    title="JobPulseAI API",
    description="API pour l'analyse de CV, matching, recommandations et prédiction de salaire",
    version="1.0.0"
)
init_db()
# Pré-charger les données en mémoire au démarrage
from app.utils.data_loader import load_postings
print("🔥 Pré-chargement des données...")
load_postings(nrows=3000)
print("✅ Données pré-chargées en mémoire")
app.include_router(history.router)
app.include_router(chatbot.router)
app.include_router(conversations.router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(cv.router)
app.include_router(matching.router)
app.include_router(skill_gap.router)
app.include_router(recommendations.router)
app.include_router(salary.router)
app.include_router(jobs.router)
app.include_router(stats.router)

@app.get("/")
async def root():
    return {"message": "Welcome to JobPulseAI API"}