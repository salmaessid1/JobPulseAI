# backend/app/utils/data_loader.py
"""
Utilitaire pour charger les données avec fallback pour le cloud.
Cherche le fichier dans data/raw, data/processed, puis data/samples.
"""
import os
import pandas as pd
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


def get_data_path() -> Optional[str]:
    """Retourne le premier fichier de données disponible."""
    candidates = [
        os.path.join(PROJECT_ROOT, "data", "processed", "postings_sample_50000.csv"),
        os.path.join(PROJECT_ROOT, "data", "raw", "postings.csv"),
        os.path.join(PROJECT_ROOT, "data", "samples", "postings_sample_cloud.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def load_postings(nrows: int = None, low_memory: bool = False) -> pd.DataFrame:
    """Charge les offres avec fallback automatique."""
    path = get_data_path()
    if path is None:
        print("⚠️ Aucun fichier de données trouvé")
        return pd.DataFrame()
    
    print(f"📂 Chargement depuis : {path}")
    try:
        df = pd.read_csv(path, nrows=nrows, low_memory=low_memory)
        print(f"✅ {len(df)} offres chargées")
        return df
    except Exception as e:
        print(f"❌ Erreur de chargement : {e}")
        return pd.DataFrame()