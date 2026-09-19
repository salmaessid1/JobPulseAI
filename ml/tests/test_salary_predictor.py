# ml/tests/test_salary_predictor.py
# Test du prédicteur de salaire

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inference.predict_salary import SalaryPredictor

def test_predict():
    # Vérifier que le modèle existe
    if not os.path.exists("models/salary_model.pkl"):
        print("⚠️ Modèle de salaire introuvable. Exécute d'abord le script d'entraînement.")
        return

    predictor = SalaryPredictor()
    job = {
        "title": "Data Scientist",
        "formatted_experience_level": "Mid-Level",
        "remote_allowed": 1,
        "work_type": "Full-time",
        "location": "New York, NY",
        "min_salary": 80000,
        "max_salary": 120000
    }
    result = predictor.predict_range(job)
    print("✅ Test prédiction salaire réussi.")
    print(f"Salaire prédit : {result['predicted_salary']:.2f}")
    print(f"Fourchette : {result['min_range']:.2f} - {result['max_range']:.2f}")

if __name__ == "__main__":
    test_predict()