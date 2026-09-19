# tests/test_e2e.py
"""
Tests end-to-end pour JobPulseAI
Vérifie que tous les endpoints fonctionnent correctement.
"""
import requests
import json
from pathlib import Path
from datetime import datetime

API = "http://127.0.0.1:8000"
RESULTS = []

def log(name, success, message=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {name} : {message}")
    RESULTS.append((name, success, message))

def test_api_health():
    try:
        r = requests.get(f"{API}/stats/global", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log("API Health", True, f"{data['total_jobs']:,} offres, {data['unique_skills']} compétences")
        else:
            log("API Health", False, f"Status {r.status_code}")
    except Exception as e:
        log("API Health", False, str(e))

def test_cv_upload():
    pdf_path = Path("data/cv_samples/Resume.pdf")
    if not pdf_path.exists():
        log("CV Upload", False, f"Fichier introuvable : {pdf_path}")
        return
    try:
        with open(pdf_path, "rb") as f:
            r = requests.post(f"{API}/cv/upload", files={"file": f}, timeout=30)
        if r.status_code == 200:
            profile = r.json()['profile']
            log("CV Upload", True, f"{len(profile['skills'])} compétences, séniorité: {profile['seniority']}")
        else:
            log("CV Upload", False, f"Status {r.status_code}")
    except Exception as e:
        log("CV Upload", False, str(e))

def test_matching():
    payload = {"cv_text": "Python, SQL, Machine Learning, Docker", 
               "job_text": "Python, SQL, AWS, Docker, Kubernetes"}
    try:
        r = requests.post(f"{API}/matching/", json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            log("Matching", True, f"Score {data['score']}%, {data['common_count']} compétences communes")
        else:
            log("Matching", False, f"Status {r.status_code}")
    except Exception as e:
        log("Matching", False, str(e))

def test_skill_gap():
    profile = {"skills": ["python", "sql", "pandas"]}
    job_text = "Data Scientist with Python, SQL, AWS, Docker, Machine Learning"
    payload = {"profile": profile, "job_text": job_text}
    try:
        r = requests.post(f"{API}/skill-gap/", json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            log("Skill Gap", True, f"{data['total_missing']} compétences manquantes")
        else:
            log("Skill Gap", False, f"Status {r.status_code}")
    except Exception as e:
        log("Skill Gap", False, str(e))

def test_recommendations():
    profile = {
        "name": "Test User",
        "skills": ["python", "sql", "docker", "git"],
        "domains": ["data_science"],
        "seniority": "mid",
        "categorized_skills": {"programming_languages": ["python", "sql"]}
    }
    payload = {"profile": profile, "top_n": 5}
    try:
        r = requests.post(f"{API}/recommendations/", json=payload, timeout=20)
        if r.status_code == 200:
            recs = r.json()
            log("Recommendations", True, f"{len(recs)} offres recommandées")
        else:
            log("Recommendations", False, f"Status {r.status_code}")
    except Exception as e:
        log("Recommendations", False, str(e))

def test_salary():
    payload = {
        "title": "Data Scientist",
        "formatted_experience_level": "Mid-Level",
        "remote_allowed": 1,
        "work_type": "Full-time",
        "location": "New York, NY",
        "min_salary": 80000,
        "max_salary": 120000
    }
    try:
        r = requests.post(f"{API}/salary/predict", json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            log("Salary", True, f"{data['predicted_salary']:.0f} USD")
        else:
            log("Salary", False, f"Status {r.status_code}")
    except Exception as e:
        log("Salary", False, str(e))

def run_all():
    print("=" * 60)
    print(f"🧪 Tests JobPulseAI - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    test_api_health()
    test_cv_upload()
    test_matching()
    test_skill_gap()
    test_recommendations()
    test_salary()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    passed = sum(1 for _, s, _ in RESULTS if s)
    total = len(RESULTS)
    for name, success, msg in RESULTS:
        icon = "✅" if success else "❌"
        print(f"{icon} {name} : {msg}")
    print(f"\n{passed}/{total} tests passés ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés !")
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")

if __name__ == "__main__":
    run_all()