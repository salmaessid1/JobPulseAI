import pandas as pd
from sklearn.model_selection import train_test_split

SECTORS = {
    "Tech": ["developer", "engineer", "software", "frontend", "backend"],
    "Data": ["data scientist", "data analyst", "machine learning", "ml engineer"],
    "Finance": ["finance", "banking", "fintech", "investment"],
    "Santé": ["health", "medical", "pharma", "clinical"],
    "Marketing": ["marketing", "seo", "content", "social media"],
    "Vente": ["sales", "account executive", "business development"],
}

def classify_sector(title):
    if not title or pd.isna(title): return "Autre"
    t = str(title).lower()
    for sector, kws in SECTORS.items():
        for kw in kws:
            if kw in t: return sector
    return "Autre"

# Charger les offres
df = pd.read_csv("data/processed/postings_sample_50000.csv", nrows=10000)
df = df.dropna(subset=["title", "description"])
df["sector"] = df["title"].apply(classify_sector)
df = df[df["sector"] != "Autre"]  # Garder que les labels connus

# Split
train, test = train_test_split(df, test_size=0.2, random_state=42)
train.to_csv("data/processed/train_classification.csv", index=False)
test.to_csv("data/processed/test_classification.csv", index=False)
print(f"Train: {len(train)} | Test: {len(test)}")
print(train["sector"].value_counts())