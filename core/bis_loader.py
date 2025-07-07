# core/bis_loader.py – v2025-07-08 (robuste)
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
        try:
            df = pd.read_csv(file)
            df["source_file"] = file.name  # trace d'origine
            df_list.append(df)
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {file.name} : {e}")

    if not df_list:
        # Renvoie un DataFrame vide avec les bonnes colonnes pour éviter les crashs
        empty_cols = ["Frequency", "Type", "Basket", "Unit", "Date", "Country", "Value", "source_file"]
        return pd.DataFrame(columns=empty_cols)

    full_df = pd.concat(df_list, ignore_index=True)
    return full_df

# ------------------------------------------------------------------ #
# 2. Extraction des options de filtre                               #
# ------------------------------------------------------------------ #

def get_filter_options(df: pd.DataFrame) -> dict:
    """Retourne un dictionnaire des options possibles pour chaque filtre."""
    return {
        "Frequency": sorted(df["Frequency"].dropna().unique().tolist()) if "Frequency" in df.columns else [],
        "Type": sorted(df["Type"].dropna().unique().tolist()) if "Type" in df.columns else [],
        "Basket": sorted(df["Basket"].dropna().unique().tolist()) if "Basket" in df.columns else [],
        "Unit": sorted(df["Unit"].dropna().unique().tolist()) if "Unit" in df.columns else [],
        "Date": sorted(df["Date"].dropna().unique().tolist()) if "Date" in df.columns else [],
        "Country": sorted(df["Country"].dropna().unique().tolist()) if "Country" in df.columns else [],
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
