# ml/nlp/skill_gap.py
from .skills_dictionary import get_skill_category
from .extract_skills import extract_skills

def compute_skill_gap(profile: dict, job_skills: list) -> dict:
    cv_skills = set(s.lower().strip() for s in profile.get("skills", []))
    job_set = set(s.lower().strip() for s in job_skills)
    missing = job_set - cv_skills
    gap_by_category = {}
    for skill in missing:
        cat = get_skill_category(skill)
        gap_by_category.setdefault(cat, []).append(skill)
    for cat in gap_by_category:
        gap_by_category[cat].sort()
    return {
        "gap_by_category": gap_by_category,
        "total_missing": len(missing),
        "missing_skills": sorted(list(missing)),
        "summary": f"Il manque {len(missing)} compétence(s) pour ce poste."
    }

def compute_skill_gap_from_texts(profile: dict, job_text: str) -> dict:
    job_result = extract_skills(job_text)
    return compute_skill_gap(profile, job_result["skills"])
