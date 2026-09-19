# ml/tests/test_resume_analyzer.py
# Test du module d'analyse de CV

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.resume_analyzer import analyze_resume

def test_analyze_resume():
    # Utilise le CV exemple présent dans data/cv_samples/Resume.pdf
    pdf_path = os.path.join("data", "cv_samples", "Resume.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"⚠️ Fichier {pdf_path} introuvable. Test ignoré.")
        return
    
    profile = analyze_resume(pdf_path)
    
    # Vérifications basiques
    assert "name" in profile
    assert "skills" in profile
    assert "categorized_skills" in profile
    assert "domains" in profile
    assert "seniority" in profile
    
    print("✅ Test d'analyse de CV réussi.")
    print(f"Nom extrait : {profile['name']}")
    print(f"Compétences : {profile['skills']}")
    print(f"Domaines : {profile['domains']}")

if __name__ == "__main__":
    test_analyze_resume()