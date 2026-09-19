# ml/tests/test_extract_skills.py
# Tests unitaires pour le module d'extraction de compétences

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp.extract_skills import extract_skills
from nlp.skills_dictionary import SKILLS, get_skill_category

def test_extract_skills_basic():
    text = "Data Scientist experienced in Python, SQL, Pandas, TensorFlow, Docker and AWS."
    result = extract_skills(text)
    expected_skills = ["aws", "docker", "pandas", "python", "sql", "tensorflow"]
    assert sorted(result["skills"]) == sorted(expected_skills)
    assert "programming_languages" in result["categorized"]
    assert "python_libraries" in result["categorized"]
    assert "cloud_devops" in result["categorized"]

def test_extract_skills_with_phrases():
    text = "Expert en machine learning et deep learning, avec une maîtrise de la computer vision."
    result = extract_skills(text)
    assert "machine learning" in result["skills"]
    assert "deep learning" in result["skills"]
    assert "computer vision" in result["skills"]
    assert "learning" not in result["skills"]

def test_extract_skills_empty():
    result = extract_skills("")
    assert result["skills"] == []
    assert result["categorized"] == {}

def test_extract_skills_no_skills():
    text = "Ce texte ne contient aucune compétence connue."
    result = extract_skills(text)
    assert result["skills"] == []
    assert result["categorized"] == {}

def test_get_skill_category():
    assert get_skill_category("python") == "programming_languages"
    assert get_skill_category("pandas") == "python_libraries"
    assert get_skill_category("aws") == "cloud_devops"
    assert get_skill_category("inconnu") == "other"

if __name__ == "__main__":
    test_extract_skills_basic()
    test_extract_skills_with_phrases()
    test_extract_skills_empty()
    test_extract_skills_no_skills()
    test_get_skill_category()
    print("✅ Tous les tests sont passés.")