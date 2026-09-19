# ml/nlp/job_matcher.py
from .extract_skills import extract_skills

def match_cv_job(cv_skills: list, job_skills: list) -> dict:
    cv_set = set(s.lower().strip() for s in cv_skills)
    job_set = set(s.lower().strip() for s in job_skills)
    common = cv_set & job_set
    missing = job_set - cv_set
    extra = cv_set - job_set
    score = len(common) / len(job_set) if job_set else 0.0
    score_percent = round(score * 100, 2)
    return {
        "score": score_percent,
        "common_skills": sorted(list(common)),
        "missing_skills": sorted(list(missing)),
        "extra_skills": sorted(list(extra)),
        "cv_skills_count": len(cv_set),
        "job_skills_count": len(job_set),
        "common_count": len(common)
    }

def match_cv_job_from_texts(cv_text: str, job_text: str) -> dict:
    cv_result = extract_skills(cv_text)
    job_result = extract_skills(job_text)
    return match_cv_job(cv_result["skills"], job_result["skills"])

def match_cv_job_from_profile(profile: dict, job_text: str) -> dict:
    cv_skills = profile.get("skills", [])
    job_result = extract_skills(job_text)
    return match_cv_job(cv_skills, job_result["skills"])

# Nouvelle fonction pour le matching sémantique
def match_semantic(cv_text, job_text, model_name='all-MiniLM-L6-v2'):
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer(model_name)
        emb_cv = model.encode(cv_text, convert_to_tensor=True)
        emb_job = model.encode(job_text, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(emb_cv, emb_job).item()
        return round(similarity * 100, 2)
    except:
        return None  # si SentenceTransformers pas installé