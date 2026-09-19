#nettoyage des offres
from pathlib import Path
import re
import sys

import pandas as pd

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

sys.path.append(str(PROJECT_ROOT))

from ml.preprocessing.skills_dictionary import SKILLS


RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def normalize_column_name(column: str) -> str:
    column = column.strip().lower()
    column = re.sub(r"[^a-z0-9]+", "_", column)
    return column.strip("_")


def clean_text(value) -> str:
    if pd.isna(value):
        return ""

    text = str(value).lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text: str) -> list[str]:
    cleaned_text = clean_text(text)

    detected = []

    for skill in SKILLS:
        pattern = rf"(?<!\w){re.escape(skill.lower())}(?!\w)"

        if re.search(pattern, cleaned_text):
            detected.append(skill)

    return sorted(set(detected))


def find_first_existing_column(
    dataframe: pd.DataFrame,
    candidates: list[str]
) -> str | None:

    for candidate in candidates:
        if candidate in dataframe.columns:
            return candidate

    return None


def load_jobs_sample() -> pd.DataFrame:
    sample_file = PROCESSED_DIR / "postings_sample_50000.csv"

    if sample_file.exists():
        print(f"Chargement : {sample_file.name}")
        return pd.read_csv(sample_file, low_memory=False)

    source_file = RAW_DIR / "postings.csv"

    if not source_file.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {source_file}"
        )

    print("Création d'un échantillon de 50 000 offres...")

    return pd.read_csv(
        source_file,
        nrows=50_000,
        low_memory=False
    )


def clean_jobs() -> pd.DataFrame:
    df = load_jobs_sample()

    print("Dimensions initiales :", df.shape)

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    print("Colonnes détectées :")
    print(df.columns.tolist())

    title_column = find_first_existing_column(
        df,
        [
            "title",
            "job_title",
            "position",
            "name"
        ]
    )

    description_column = find_first_existing_column(
        df,
        [
            "description",
            "job_description",
            "formatted_work_type",
            "skills_desc"
        ]
    )

    company_column = find_first_existing_column(
        df,
        [
            "company_name",
            "company",
            "employer_name"
        ]
    )

    location_column = find_first_existing_column(
        df,
        [
            "location",
            "job_location",
            "city"
        ]
    )

    salary_column = find_first_existing_column(
        df,
        [
            "normalized_salary",
            "salary",
            "salary_in_usd",
            "max_salary",
            "med_salary"
        ]
    )

    if title_column is None:
        raise ValueError(
            "Aucune colonne de titre de poste n'a été trouvée."
        )

    selected_columns = [title_column]

    for column in [
        description_column,
        company_column,
        location_column,
        salary_column
    ]:
        if column is not None:
            selected_columns.append(column)

    clean_df = df[selected_columns].copy()

    rename_mapping = {
        title_column: "job_title"
    }

    if description_column:
        rename_mapping[description_column] = "description"

    if company_column:
        rename_mapping[company_column] = "company"

    if location_column:
        rename_mapping[location_column] = "location"

    if salary_column:
        rename_mapping[salary_column] = "salary"

    clean_df = clean_df.rename(columns=rename_mapping)

    clean_df = clean_df.drop_duplicates()

    clean_df["job_title"] = (
        clean_df["job_title"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    clean_df = clean_df[
        clean_df["job_title"] != ""
    ]

    if "description" not in clean_df.columns:
        clean_df["description"] = ""

    clean_df["description_clean"] = (
        clean_df["description"]
        .apply(clean_text)
    )

    clean_df["skills"] = (
        clean_df["description_clean"]
        .apply(extract_skills)
    )

    clean_df["skills_count"] = (
        clean_df["skills"]
        .apply(len)
    )

    clean_df["skills_text"] = (
        clean_df["skills"]
        .apply(lambda values: ", ".join(values))
    )

    if "company" in clean_df.columns:
        clean_df["company"] = (
            clean_df["company"]
            .fillna("unknown")
            .astype(str)
            .str.strip()
        )

    if "location" in clean_df.columns:
        clean_df["location"] = (
            clean_df["location"]
            .fillna("unknown")
            .astype(str)
            .str.strip()
        )

    if "salary" in clean_df.columns:
        clean_df["salary"] = pd.to_numeric(
            clean_df["salary"],
            errors="coerce"
        )

    output_file = PROCESSED_DIR / "clean_jobs.csv"

    clean_df.to_csv(
        output_file,
        index=False
    )

    print("Dimensions finales :", clean_df.shape)
    print(f"Fichier créé : {output_file}")

    return clean_df


if __name__ == "__main__":
    result = clean_jobs()

    print(result.head())
    print(result["skills_text"].head())