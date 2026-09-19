# backend/app/services/salary_service.py
import os
import sys
import joblib
import pandas as pd
from typing import Dict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "salary_model.pkl")
ENCODER_PATH = os.path.join(PROJECT_ROOT, "models", "salary_encoders.pkl")
SCALER_PATH = os.path.join(PROJECT_ROOT, "models", "salary_scaler.pkl")


class SalaryPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")

        self.model = joblib.load(MODEL_PATH)
        self.encoders = joblib.load(ENCODER_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        print(f"✅ Modèle salaire chargé ({os.path.getmtime(MODEL_PATH)})")

    def predict_range(self, features: Dict) -> Dict:
        df = pd.DataFrame([features])

        # Gérer les valeurs manquantes
        for col in ["title", "formatted_experience_level", "work_type", "location"]:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                df[col] = "Unknown"

        # Encoder les catégories
        for col in ["title", "formatted_experience_level", "work_type", "location"]:
            le = self.encoders[col]
            try:
                df[col] = le.transform(df[col].astype(str))
            except ValueError:
                df[col] = 0  # Catégorie inconnue

        # Scaler
        num_cols = ["min_salary", "max_salary"]
        for col in num_cols:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                df[col] = 0
        df[num_cols] = self.scaler.transform(df[num_cols])

        # Prédiction
        X = df[["title", "formatted_experience_level", "remote_allowed", "work_type",
                "location", "min_salary", "max_salary"]].values
        pred = float(self.model.predict(X)[0])

        # Sécurité : si négatif, retourner une estimation plausible
        if pred < 0:
            pred = abs(pred) * 0.5  # Fallback

        return {
            "predicted_salary": round(pred, 2),
            "min_range": round(pred * 0.85, 2),
            "max_range": round(pred * 1.15, 2),
        }


# ⚠️ IMPORTANT : recharger le modèle à CHAQUE appel pour prendre en compte les mises à jour
def predict_salary(job_features: Dict) -> Dict:
    """Charge le modèle frais à chaque appel (évite les problèmes de cache)."""
    predictor = SalaryPredictor()
    return predictor.predict_range(job_features)