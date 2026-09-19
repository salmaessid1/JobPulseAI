# ml/nlp/resume_parser.py
import pdfplumber
from .text_cleaner import clean_text

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'extraction du PDF : {e}")
    return text.strip()

def extract_name(text: str) -> str:
    lines = text.splitlines()
    for line in lines:
        if line.strip():
            return line.strip()
    return "Inconnu"

def extract_sections(text: str) -> dict:
    return {"experience": "", "education": "", "skills": "", "other": text}

def parse_resume(pdf_path: str) -> dict:
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned = clean_text(raw_text)
    name = extract_name(raw_text)
    sections = extract_sections(raw_text)
    return {
        "name": name,
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "sections": sections
    }
