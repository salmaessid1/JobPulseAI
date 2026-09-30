# ml/nlp/test_semantic.py
from ml.nlp.semantic_matcher import semantic_similarity

tests = [
    (
        "Je suis développeur Python avec 5 ans d'expérience en Data Science.",
        "Nous cherchons un ingénieur Python expérimenté en analyse de données.",
    ),
    (
        "Je suis développeur Python avec 5 ans d'expérience en Data Science.",
        "Nous cherchons un chef cuisinier pour notre restaurant gastronomique.",
    ),
    (
        "Expert en machine learning et deep learning, maîtrise de TensorFlow.",
        "Poste de Data Scientist spécialisé en modèles prédictifs et IA.",
    ),
]

print("=" * 70)
print("TEST DE SIMILARITÉ SÉMANTIQUE")
print("=" * 70)

for i, (cv, job) in enumerate(tests, 1):
    score = semantic_similarity(cv, job)
    print(f"\n--- Test {i} ---")
    print(f"CV  : {cv[:60]}...")
    print(f"Job : {job[:60]}...")
    print(f"🎯 Score : {score}%")
    # Interprétation
    if score > 60:
        print("   ✅ Très bon match")
    elif score > 40:
        print("   🟡 Match moyen")
    else:
        print("   🔴 Faible match")