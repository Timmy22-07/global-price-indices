# core/bis_loader.py – v2025-07-07
# ---------------------------------------------------------------------
# BIS – Real Effective Exchange Rates (REER)
# • Chargement depuis plusieurs fichiers CSV
# • Options dynamiques : Frequency, Type, Basket, Unit
# • Filtrage basé sur les choix utilisateur
# ---------------------------------------------------------------------

from pathlib import Path
import pandas as pd

# Dossier contenant les fichiers CSV REER
DATA_DIR = Path("data/raw/bis_reer")

# ------------------------------------------------------------------ #
# 1. Chargement des fichiers BIS REER                               #
# ------------------------------------------------------------------ #

def load_bis_reer_data() -> pd.DataFrame:
    """Charge tous les fichiers CSV de BIS REER dans un seul DataFrame."""
    all_files = list(DATA_DIR.glob("*.csv"))
    df_list = []
    for file in all_files:
        df = pd.read_csv(file)
        df["source_file"] = file.name  # trace d'origine
        df_list.append(df)
    full_df = pd.concat(df_list, ignore_index=True)
    return full_df

# ------------------------------------------------------------------ #
# 2. Extraction des options de filtre                               #
# ------------------------------------------------------------------ #

def get_filter_options(df: pd.DataFrame) -> dict:
    """Retourne un dictionnaire des options possibles pour chaque filtre."""
    return {
        "Frequency": sorted(df["Frequency"].dropna().unique().tolist()),
        "Type": sorted(df["Type"].dropna().unique().tolist()),
        "Basket": sorted(df["Basket"].dropna().unique().tolist()),
        "Unit": sorted(df["Unit"].dropna().unique().tolist()),
        "Date": sorted(df["Date"].dropna().unique().tolist()),
        "Country": sorted(df["Country"].dropna().unique().tolist()),
    }

# ------------------------------------------------------------------ #
# 3. Filtrage selon les paramètres sélectionnés                     #
# ------------------------------------------------------------------ #

def filter_bis_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Filtre les données BIS REER selon les paramètres donnés."""
    filtered = df.copy()
    for key, values in filters.items():
        if values and key in filtered.columns:
            filtered = filtered[filtered[key].isin(values)]
    return filtered.reset_index(drop=True)
