# ml/tests/test_job_matcher.py
# Test du module de matching

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.job_matcher import match_cv_job, match_cv_job_from_texts, match_cv_job_from_profile
from nlp.resume_analyzer import analyze_resume

def test_match_cv_job():
    cv_skills = ["python", "sql", "pandas", "docker"]
    job_skills = ["python", "sql", "docker", "aws", "kubernetes"]
    result = match_cv_job(cv_skills, job_skills)
    assert result["score"] == 60.0
    assert "python" in result["common_skills"]
    assert "aws" in result["missing_skills"]
    print("✅ Test match_cv_job réussi.")
    print(f"Score: {result['score']}%")
    print(f"Communes: {result['common_skills']}")
    print(f"Manquantes: {result['missing_skills']}")

def test_match_cv_job_from_texts():
    cv_text = "Data Scientist with Python, SQL, and Pandas."
    job_text = "Looking for a Data Scientist with Python, SQL, Docker, and AWS."
    result = match_cv_job_from_texts(cv_text, job_text)
    print("✅ Test match_cv_job_from_texts réussi.")
    print(f"Score: {result['score']}%")
    print(f"Communes: {result['common_skills']}")
    print(f"Manquantes: {result['missing_skills']}")

def test_match_with_real_cv():
    cv_pdf = os.path.join("data", "cv_samples", "Resume.pdf")
    if not os.path.exists(cv_pdf):
        print("⚠️ CV exemple introuvable. Test ignoré.")
        return
    
    profile = analyze_resume(cv_pdf)
    job_text = "We are hiring a Full Stack Developer with expertise in JavaScript, TypeScript, React, Node.js, PostgreSQL, Docker, and AWS."
    result = match_cv_job_from_profile(profile, job_text)
    print("✅ Test avec CV réel réussi.")
    print(f"Score: {result['score']}%")
    print(f"Compétences communes: {result['common_skills']}")
    print(f"Compétences manquantes: {result['missing_skills']}")

if __name__ == "__main__":
    test_match_cv_job()
    test_match_cv_job_from_texts()
    test_match_with_real_cv()