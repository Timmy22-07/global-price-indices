# core/numbeo_loader.py – v2025‑07‑07 fixed
# ---------------------------------------------------------------------
# Loader adapté au format réel du fichier Numbeo (nommé « name »)
# ✅ Utilise « name » comme identifiant de région
# ✅ Exclut les colonnes inutiles (« id_city », « status », etc.)
# ✅ Utilisé par numbeo_block.py
# ---------------------------------------------------------------------

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = Path("data/raw/numbeo/numbeo.db")
FALLBACK_CSV = Path("data/raw/numbeo/numbeo_fallback.csv")  # fallback optionnel

# ------------------------------------------------------------------ #
# 1. Chargement (DB ou fallback CSV)                                 #
# ------------------------------------------------------------------ #

@st.cache_data(show_spinner=False)
def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Charge les données de Numbeo (nommée 'name')."""
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
                if len(tables) == 0:
                    raise ValueError("Aucune table trouvée dans la base de données.")
                df = pd.read_sql(f"SELECT * FROM {tables[0]};", conn)  # prend la 1re table trouvée
                df.columns = df.columns.str.strip()
                return df
        except Exception as e:
            st.warning(f"⚠️ Erreur lecture DB Numbeo ({e}) – tentative CSV…")

    if FALLBACK_CSV.exists():
        st.info("Chargement du fichier CSV de secours pour Numbeo…")
        return pd.read_csv(FALLBACK_CSV)

    raise FileNotFoundError("Aucune source valide pour les données Numbeo (DB ou CSV).")

# ------------------------------------------------------------------ #
# 2. Sélecteurs : régions + variables                                #
# ------------------------------------------------------------------ #

def get_city_options(df: pd.DataFrame) -> list[str]:
    if "name" not in df.columns:
        raise ValueError("La colonne 'name' est absente des données Numbeo.")
    return sorted(df["name"].dropna().astype(str).str.strip().unique())

def get_variable_options(df: pd.DataFrame) -> list[str]:
    exclude = {"id_city", "name", "status"}
    return [col for col in df.columns if col not in exclude]

# ------------------------------------------------------------------ #
# 3. Filtrage                                                        #
# ------------------------------------------------------------------ #

def filter_numbeo_data(df: pd.DataFrame, regions: list[str], variables: list[str]) -> pd.DataFrame:
    if "name" not in df.columns:
        raise ValueError("Colonne 'name' introuvable.")
    if not regions:
        regions = df["name"].dropna().unique()
    filtered = df[df["name"].isin(regions)].copy()
    cols = ["name"] + (["status"] if "status" in df.columns else []) + variables
    return filtered[cols].reset_index(drop=True)
