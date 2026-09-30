# backend/preload_models.py
"""
Script exécuté au démarrage pour pré-télécharger les modèles Sentence-BERT.
"""
import os
import sys

def preload():
    try:
        print("🔄 Pré-téléchargement du modèle Sentence-BERT...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Modèle Sentence-BERT prêt")
        return True
    except Exception as e:
        print(f"⚠️ Impossible de pré-charger Sentence-BERT : {e}")
        return False

if __name__ == "__main__":
    preload()