import os
import torch
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml', 'models', 'job_classifier')

class JobClassifier:
    def __init__(self):
        if not os.path.exists(MODEL_DIR):
            raise FileNotFoundError(f"Modèle non trouvé : {MODEL_DIR}")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        self.model.eval()
        self.le = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

    def predict(self, text):
        inputs = self.tokenizer(
            text, truncation=True, padding=True,
            max_length=128, return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
            probs = torch.softmax(outputs.logits, dim=1)[0].tolist()
        return {
            "sector": self.le.classes_[pred],
            "confidence": round(probs[pred] * 100, 2),
            "all_scores": {
                self.le.classes_[i]: round(p * 100, 2)
                for i, p in enumerate(probs)
            }
        }

_classifier = None
def classify_job(text: str):
    global _classifier
    if _classifier is None:
        _classifier = JobClassifier()
    return _classifier.predict(text)