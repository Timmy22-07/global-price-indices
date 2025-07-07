# core/numbeo_loader.py – v2025-07-08 FINAL
# ------------------------------------------------------------
# • Chargement robuste de la base SQLite (ou fallback CSV)
# • Extraction dynamique des régions et variables
# • Filtrage basé sur régions + variables
# ------------------------------------------------------------

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# 📂 Chemins vers les fichiers
DB_PATH = Path("data/raw/numbeo/numbeo.db")
FALLBACK_CSV = Path("data/raw/numbeo/numbeo_fallback.csv")  # facultatif

# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """
    Charge les données de Numbeo depuis la base SQLite (table principale).
    Utilise un CSV de secours si la base échoue.
    """
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
                if "cities" not in tables:
                    raise ValueError(f"❌ Table 'cities' non trouvée. Tables disponibles : {tables}")
                df = pd.read_sql("SELECT * FROM cities;", conn)
                df.columns = df.columns.str.strip()
                return df
        except Exception as e:
            st.warning(f"⚠️ Échec de lecture du fichier SQLite ({e}). Tentative avec CSV…")

    if FALLBACK_CSV.exists():
        st.info("📄 Chargement du CSV de secours pour Numbeo.")
        return pd.read_csv(FALLBACK_CSV)

    raise FileNotFoundError("Aucune source valide trouvée pour les données Numbeo.")

# ─────────────────────────────────────────────────────────────
def get_city_options(df: pd.DataFrame) -> list[str]:
    """
    Retourne la liste triée des régions (colonne 'name').
    """
    if "name" not in df.columns:
        raise ValueError("🧭 Colonne 'name' manquante dans les données Numbeo.")
    return sorted(df["name"].dropna().astype(str).str.strip().unique())

# ─────────────────────────────────────────────────────────────
def get_variable_options(df: pd.DataFrame) -> list[str]:
    """
    Retourne les variables disponibles à l'exception des colonnes non quantitatives.
    """
    exclude = {"id_city", "name", "status"}
    return [col for col in df.columns if col not in exclude]

# ─────────────────────────────────────────────────────────────
def filter_numbeo_data(df: pd.DataFrame, regions: list[str], variables: list[str]) -> pd.DataFrame:
    """
    Applique les filtres de régions et de variables, retourne un DataFrame propre.
    """
    if "name" not in df.columns:
        raise ValueError("🧭 Colonne 'name' manquante dans les données Numbeo.")

    if not regions:
        regions = df["name"].dropna().unique().tolist()

    subset = df[df["name"].isin(regions)].copy()
    base_cols = ["name"]
    if "status" in df.columns:
        base_cols.append("status")

    return subset[base_cols + variables].reset_index(drop=True)
