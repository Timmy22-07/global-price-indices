# core/numbeo_loader.py – v2025-07-07 d
# ------------------------------------------------------------
# Loader robuste pour la base Numbeo (.db)
# • Liste les tables via sqlite3.Cursor   (pas de pandas.read_sql)
# • Ouvre la base en lecture-seule         =>   ?mode=ro
# • Colonne "name" = identifiant de région
# ------------------------------------------------------------
from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("data/raw/numbeo/numbeo.db")


# ---------- 1. Chargement complet -----------------------------------
def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """
    Retourne la table « cities » (ou première table utilisateur)
    sous forme de DataFrame.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Numbeo DB not found at {db_path}")

    # Connexion en lecture-seule (= pas de lock gênant sous Streamlit)
    uri = f"file:{db_path.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]

        # On prend « cities » si elle existe, sinon la 1ʳᵉ table hors sqlite_*
        table = next((t for t in tables if t.lower() == "cities"), None) \
            or next((t for t in tables if not t.startswith("sqlite_")), None)

        if table is None:
            raise ValueError(f"No suitable table found in {db_path}. Tables: {tables}")

        # Lecture de la table via pandas
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)

    df.columns = df.columns.str.strip()
    return df


# ---------- 2. Helpers ----------------------------------------------
def get_region_options(df: pd.DataFrame) -> list[str]:
    if "name" not in df.columns:
        raise ValueError("'name' column not found in Numbeo dataset.")
    return sorted(df["name"].dropna().unique())


def get_variable_options(df: pd.DataFrame) -> list[str]:
    exclude = {"id_city", "name", "status"}
    return [c for c in df.columns if c not in exclude]


# ---------- 3. Filtrage ----------------------------------------------
def filter_numbeo_data(
    df: pd.DataFrame,
    regions: list[str] | None,
    variables: list[str] | None,
) -> pd.DataFrame:
    """Filtre sur régions (None = toutes) + variables choisies."""
    if regions:
        df = df[df["name"].isin(regions)].copy()

    if variables:
        keep = ["name", "status"] + variables if "status" in df.columns else ["name"] + variables
        df = df[keep]

    return df.reset_index(drop=True)
