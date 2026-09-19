# create_sample_for_cloud.py
import pandas as pd
import os

# Lire un échantillon
df = pd.read_csv("data/raw/postings.csv", nrows=500, low_memory=False)

# Garder seulement les colonnes utiles
cols = ['job_id', 'company_name', 'title', 'description', 'location',
        'formatted_experience_level', 'remote_allowed', 'work_type',
        'normalized_salary', 'min_salary', 'max_salary', 'skills_desc',
        'listed_time']
cols = [c for c in cols if c in df.columns]
df = df[cols]

# Créer le dossier si nécessaire
os.makedirs("data/samples", exist_ok=True)

# Sauvegarder
df.to_csv("data/samples/postings_sample_cloud.csv", index=False)
print(f"✅ Échantillon créé : data/samples/postings_sample_cloud.csv")
print(f"   {len(df)} lignes, {os.path.getsize('data/samples/postings_sample_cloud.csv') / 1024:.1f} Ko")