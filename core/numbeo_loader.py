# core/numbeo_loader.py – v2025-07-07 c
# ------------------------------------------------------------
# • Charge la base SQLite Numbeo   (table « cities »)
# • Renvoie la liste des régions (colonne name)
# • Filtre sur 1 ou plusieurs régions + variables
# ------------------------------------------------------------
from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("data/raw/numbeo/numbeo.db")


# ---------- 1. Chargement complet -----------------------------------
def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Retourne la table **cities** (ou la 1ʳᵉ table non système)."""
    if not db_path.exists():
        raise FileNotFoundError(f"Numbeo DB not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        tbls = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
        # On garde la première table « cities » si elle existe, sinon la première hors sqlite_sequence
        table = next((t for t in tbls if t.lower() == "cities"), None) or next(
            (t for t in tbls if not t.startswith("sqlite_")), None
        )
        if table is None:
            raise ValueError(f"No suitable table found in {db_path}. Tables: {tbls}")

        df = pd.read_sql(f"SELECT * FROM {table};", conn)

    df.columns = df.columns.str.strip()
    return df


# ---------- 2. Helpers ----------------------------------------------
def get_region_options(df: pd.DataFrame) -> list[str]:
    """Renv. la liste triée des régions (= colonne name)."""
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
    """Filtre sur régions (liste ou None = toutes) + variables choisies."""
    if regions:  # Filtre par régions
        df = df[df["name"].isin(regions)].copy()

    if variables:  # Sous-ensemble de colonnes à afficher
        keep = ["name", "status"] + variables if "status" in df.columns else ["name"] + variables
        df = df[keep]

    return df.reset_index(drop=True)
