# ml/inference/predict_salary.py
# Inférence du modèle de salaire

import joblib
import pandas as pd
import os
from typing import Dict, Union

MODEL_PATH = os.path.join("models", "salary_model.pkl")
ENCODER_PATH = os.path.join("models", "salary_encoders.pkl")
SCALER_PATH = os.path.join("models", "salary_scaler.pkl")

class SalaryPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.encoders = joblib.load(ENCODER_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def predict(self, job_features: Dict) -> float:
        """
        Prédit le salaire normalisé à partir d'un dictionnaire de caractéristiques.
        Exemple d'input:
        {
            "title": "Data Scientist",
            "formatted_experience_level": "Mid-Level",
            "remote_allowed": 1,
            "work_type": "Full-time",
            "location": "New York, NY",
            "min_salary": 80000,
            "max_salary": 120000
        }
        """
        # Créer un DataFrame à partir du dict
        df = pd.DataFrame([job_features])

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
                # Si la catégorie est inconnue, on la remplace par la plus fréquente (ou 0)
                df[col] = 0

        # Standardiser les colonnes numériques
        num_cols = ["min_salary", "max_salary"]
        for col in num_cols:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                df[col] = 0  # Valeur par défaut
        # On scale les valeurs
        df[num_cols] = self.scaler.transform(df[num_cols])

        # Extraire les features dans l'ordre
        X = df[["title", "formatted_experience_level", "remote_allowed", "work_type",
                "location", "min_salary", "max_salary"]].values

        pred = self.model.predict(X)[0]
        return pred

    def predict_range(self, job_features: Dict) -> Dict:
        """
        Retourne une fourchette de salaire (min, max) autour de la prédiction.
        """
        pred = self.predict(job_features)
        # Définir un intervalle de ±15%
        return {
            "predicted_salary": round(pred, 2),
            "min_range": round(pred * 0.85, 2),
            "max_range": round(pred * 1.15, 2)
        }

# Fonction utilitaire pour une prédiction rapide
def predict_salary(job_features: Dict) -> Dict:
    predictor = SalaryPredictor()
    return predictor.predict_range(job_features)