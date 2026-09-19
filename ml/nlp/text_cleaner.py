# ml/nlp/text_cleaner.py
import re
import unicodedata

def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_words(text: str) -> list:
    return text.split() if text else []
