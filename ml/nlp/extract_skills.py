# ml/nlp/extract_skills.py
import re
from .skills_dictionary import SKILLS, get_skill_category
from .text_cleaner import clean_text

def extract_skills(text: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"skills": [], "categorized": {}}
    sorted_skills = sorted(SKILLS, key=len, reverse=True)
    found = set()
    remaining_text = cleaned
    for skill in sorted_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, remaining_text):
            found.add(skill)
            remaining_text = re.sub(pattern, ' ' * len(skill), remaining_text)
    skills_list = sorted(list(found))
    categorized = {}
    for skill in skills_list:
        cat = get_skill_category(skill)
        categorized.setdefault(cat, []).append(skill)
    return {"skills": skills_list, "categorized": categorized}

def extract_skills_from_list(texts: list) -> list:
    return [extract_skills(t) for t in texts]
