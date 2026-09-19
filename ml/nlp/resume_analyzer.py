# ml/nlp/resume_analyzer.py
from .extract_skills import extract_skills
from .resume_parser import parse_resume

def analyze_resume(pdf_path: str) -> dict:
    parsed = parse_resume(pdf_path)
    skills_result = extract_skills(parsed["cleaned_text"])
    skills = skills_result["skills"]
    categorized = skills_result["categorized"]
    domains = [cat for cat, sk in categorized.items() if len(sk) >= 2]
    seniority = "junior"
    return {
        "name": parsed["name"],
        "skills": skills,
        "categorized_skills": categorized,
        "domains": domains,
        "seniority": seniority,
        "sections": parsed["sections"]
    }
