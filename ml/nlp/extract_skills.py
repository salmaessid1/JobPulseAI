# ml/nlp/extract_skills.py
import re
from .skills_dictionary import SKILLS, get_skill_category
from .text_cleaner import clean_text

def _build_pattern(skill: str) -> str:
    """Construit une regex adaptée selon le début/fin de la compétence."""
    escaped = re.escape(skill)
    # Si la compétence commence par un caractère alphanumérique -> \b à gauche
    left = r'\b' if skill[0].isalnum() else r'(?<!\w)'
    # Si elle finit par un caractère alphanumérique -> \b à droite
    # Sinon (ex: "c++", "gcp.") on utilise un lookahead négatif
    right = r'\b' if skill[-1].isalnum() else r'(?!\w)'
    return left + escaped + right

def extract_skills(text: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"skills": [], "categorized": {}}

    # Trier par longueur décroissante pour matcher "machine learning" avant "learning"
    sorted_skills = sorted(SKILLS, key=len, reverse=True)
    found = set()
    remaining_text = cleaned

    for skill in sorted_skills:
        pattern = _build_pattern(skill)
        if re.search(pattern, remaining_text):
            found.add(skill)
            # Neutraliser pour éviter les doublons sur des sous-chaînes
            remaining_text = re.sub(pattern, ' ' * len(skill), remaining_text)

    skills_list = sorted(list(found))
    categorized = {}
    for skill in skills_list:
        cat = get_skill_category(skill)
        categorized.setdefault(cat, []).append(skill)

    return {"skills": skills_list, "categorized": categorized}

def extract_skills_from_list(texts: list) -> list:
    return [extract_skills(t) for t in texts]