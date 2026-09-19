# ml/training/train_salary_model.py
# Entraînement du modèle de prédiction de salaire (VERSION CORRIGÉE)

import pandas as pd
import numpy as np
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "salary_model.pkl")
ENCODER_PATH = os.path.join(PROJECT_ROOT, "models", "salary_encoders.pkl")
SCALER_PATH = os.path.join(PROJECT_ROOT, "models", "salary_scaler.pkl")

FEATURES = ["title", "formatted_experience_level", "remote_allowed",
            "work_type", "location", "min_salary", "max_salary"]
TARGET = "normalized_salary"


def load_data():
    print("📂 Chargement des données...")
    df = pd.read_csv(DATA_PATH, nrows=5000, low_memory=False)
    
    # Nettoyage : enlever les lignes sans salaire
    df = df.dropna(subset=[TARGET])
    
    # ✅ FILTRE CRITIQUE : garder seulement les salaires plausibles
    df = df[(df[TARGET] > 20000) & (df[TARGET] < 500000)]
    
    print(f"✅ {len(df)} offres valides après filtrage")
    return df


def preprocess(df):
    df_enc = df.copy()
    encoders = {}
    
    for col in ["title", "formatted_experience_level", "work_type", "location"]:
        le = LabelEncoder()
        df_enc[col] = df_enc[col].fillna("Unknown").astype(str)
        df_enc[col] = le.fit_transform(df_enc[col])
        encoders[col] = le
    
    scaler = StandardScaler()
    num_cols = ["min_salary", "max_salary"]
    for col in num_cols:
        df_enc[col] = df_enc[col].fillna(df_enc[col].median())
    df_enc[num_cols] = scaler.fit_transform(df_enc[num_cols])
    
    return df_enc, encoders, scaler


def main():
    df = load_data()
    X_df = df[FEATURES].copy()
    y = df[TARGET]
    
    X_enc, encoders, scaler = preprocess(X_df)
    
    X_train, X_val, y_train, y_val = train_test_split(X_enc, y, test_size=0.2, random_state=42)
    
    print("🚀 Entraînement XGBoost...")
    model = xgb.XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        random_state=42, verbosity=0
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, y_pred)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    r2 = r2_score(y_val, y_pred)
    
    print(f"📊 MAE : {mae:.2f}")
    print(f"📊 RMSE : {rmse:.2f}")
    print(f"📊 R² : {r2:.4f}")
    
    # Test rapide
    sample = X_enc.iloc[0:1]
    pred = model.predict(sample)[0]
    print(f"🎯 Test prédiction : {pred:.2f} USD (salaire réel : {y.iloc[0]:.2f})")
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("✅ Modèle sauvegardé")


if __name__ == "__main__":
    main()