# backend/app/utils/data_loader.py
"""
Charge les données avec cache en mémoire et fallback pour le cloud.
"""
import os
import pandas as pd
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Cache global
_CACHE = {}


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
    """
    Charge les offres avec CACHE EN MÉMOIRE.
    Le premier appel est lent, les suivants sont instantanés.
    """
    cache_key = f"postings_{nrows}"

    # Si déjà en cache, retourner directement
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    path = get_data_path()
    if path is None:
        print("⚠️ Aucun fichier de données trouvé")
        _CACHE[cache_key] = pd.DataFrame()
        return _CACHE[cache_key]

    print(f"📂 Chargement initial depuis : {path}")
    try:
        df = pd.read_csv(path, nrows=nrows, low_memory=low_memory)
        print(f"✅ {len(df)} offres chargées et mises en cache")
        _CACHE[cache_key] = df
        return df
    except Exception as e:
        print(f"❌ Erreur de chargement : {e}")
        _CACHE[cache_key] = pd.DataFrame()
        return _CACHE[cache_key]


def clear_cache():
    """Vide le cache."""
    _CACHE.clear()
    print("🧹 Cache vidé")