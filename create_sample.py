# create_sample.py
import pandas as pd
import os

SOURCE = "data/processed/postings_sample_50000.csv"
DEST_DIR = "backend/app/data"
DEST = os.path.join(DEST_DIR, "postings_render.csv")

os.makedirs(DEST_DIR, exist_ok=True)

print(f"📂 Lecture de {SOURCE}...")
df = pd.read_csv(SOURCE, nrows=500)
df.to_csv(DEST, index=False)

size_ko = os.path.getsize(DEST) / 1024
print(f"✅ Fichier créé : {len(df)} lignes, {size_ko:.1f} Ko")
print(f"📍 Emplacement : {os.path.abspath(DEST)}")