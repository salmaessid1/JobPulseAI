# ml/tests/test_skill_gap.py
# Test du module Skill Gap

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.skill_gap import compute_skill_gap, compute_skill_gap_from_texts
from nlp.resume_analyzer import analyze_resume

def test_skill_gap():
    profile = {
        "skills": ["python", "sql", "docker"]
    }
    job_skills = ["python", "sql", "aws", "kubernetes", "docker"]
    result = compute_skill_gap(profile, job_skills)
    assert result["total_missing"] == 2
    assert "aws" in result["missing_skills"]
    assert "kubernetes" in result["missing_skills"]
    # Vérifier les catégories (aws est dans cloud_devops, kubernetes aussi)
    assert "cloud_devops" in result["gap_by_category"]
    print("✅ Test skill_gap réussi.")
    print(result["summary"])
    print("Manquants par catégorie :", result["gap_by_category"])

def test_skill_gap_from_texts():
    cv_pdf = os.path.join("data", "cv_samples", "Resume.pdf")
    if not os.path.exists(cv_pdf):
        print("⚠️ CV exemple introuvable. Test ignoré.")
        return
    
    profile = analyze_resume(cv_pdf)
    job_text = "Full Stack Developer with JavaScript, TypeScript, React, Node.js, PostgreSQL, Docker, AWS, and Kubernetes."
    result = compute_skill_gap_from_texts(profile, job_text)
    print("✅ Test skill_gap_from_texts réussi.")
    print("Résumé :", result["summary"])
    print("Manquants par catégorie :", result["gap_by_category"])

if __name__ == "__main__":
    test_skill_gap()
    test_skill_gap_from_texts()