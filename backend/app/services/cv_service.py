# backend/app/services/cv_service.py
import os
import sys
import tempfile
from typing import Dict
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from ml.nlp.resume_analyzer import analyze_resume

from app.database import SessionLocal, AnalysisHistory


def analyze_cv_file(file_content: bytes, filename: str) -> Dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name

    try:
        profile = analyze_resume(tmp_path)
        
        # Sauvegarder dans l'historique
        try:
            db = SessionLocal()
            history = AnalysisHistory(
                user_name=profile.get('name', 'Anonyme'),
                analysis_type="cv",
                input_summary=f"CV: {filename}",
                result_data=profile,
                score=None,
            )
            db.add(history)
            db.commit()
            db.close()
        except Exception as e:
            print(f"⚠️ Impossible de sauvegarder l'historique: {e}")
        
        return profile
    finally:
        os.unlink(tmp_path)