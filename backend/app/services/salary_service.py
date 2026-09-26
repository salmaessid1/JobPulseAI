# backend/app/services/salary_service.py
import os
import sys
import joblib
import pandas as pd
from typing import Dict

# Chemins possibles pour les modèles
BACKEND_MODELS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
ROOT_MODELS = os.path.join(PROJECT_ROOT, "models")

def _find_model(name: str) -> str:
    """Cherche un modèle dans backend/app/models puis dans PROJECT_ROOT/models."""
    backend_path = os.path.join(BACKEND_MODELS, name)
    root_path = os.path.join(ROOT_MODELS, name)
    if os.path.exists(backend_path):
        print(f"✅ Modèle trouvé (backend) : {backend_path}")
        return backend_path
    if os.path.exists(root_path):
        print(f"✅ Modèle trouvé (racine) : {root_path}")
        return root_path
    raise FileNotFoundError(
        f"Modèle introuvable : {name}\n"
        f"Chemins testés :\n  - {backend_path}\n  - {root_path}"
    )

MODEL_PATH = _find_model("salary_model.pkl")
ENCODER_PATH = _find_model("salary_encoders.pkl")
SCALER_PATH = _find_model("salary_scaler.pkl")


class SalaryPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.encoders = joblib.load(ENCODER_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        print(f"✅ Modèle salaire chargé ({os.path.getmtime(MODEL_PATH)})")

    def predict_range(self, features: Dict) -> Dict:
        df = pd.DataFrame([features])

        for col in ["title", "formatted_experience_level", "work_type", "location"]:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                df[col] = "Unknown"

        for col in ["title", "formatted_experience_level", "work_type", "location"]:
            le = self.encoders[col]
            try:
                df[col] = le.transform(df[col].astype(str))
            except ValueError:
                df[col] = 0

        num_cols = ["min_salary", "max_salary"]
        for col in num_cols:
            if col not in df.columns or pd.isna(df[col].iloc[0]):
                df[col] = 0
        df[num_cols] = self.scaler.transform(df[num_cols])

        X = df[["title", "formatted_experience_level", "remote_allowed", "work_type",
                "location", "min_salary", "max_salary"]].values
        pred = float(self.model.predict(X)[0])

        if pred < 0:
            pred = abs(pred) * 0.5

        return {
            "predicted_salary": round(pred, 2),
            "min_range": round(pred * 0.85, 2),
            "max_range": round(pred * 1.15, 2),
        }


def predict_salary(job_features: Dict) -> Dict:
    predictor = SalaryPredictor()
    return predictor.predict_range(job_features)