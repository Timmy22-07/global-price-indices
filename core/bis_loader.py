# core/bis_loader.py
"""BIS REER loader ‒ supports four Excel files split by period (1994‑2025).

Fonctions clés
--------------
load_bis_reer_data()            → DataFrame long format (metadata + date + value)
get_filter_options(df)          → dictionnaire des valeurs uniques + "All" pour
                                  Reference area, Frequency, Type, Basket, Unit
filter_bis_data(df, selections) → DataFrame filtré selon selections + année
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st

# Chemin par défaut vers les fichiers BIS
default_dir = Path("data/raw/bis")

META_COLS = [
    "Dataflow ID",        # A
    "Timeseries Key",     # B
    "Frequency",          # C
    "Type",               # D
    "Basket",             # E
    "Reference area",     # F
    "Unit",               # G
]

# ------------------------------------------------------------------
# 1) LOAD & MELT
# ------------------------------------------------------------------

def load_bis_reer_data(directory: Path = default_dir) -> pd.DataFrame:
    """Charge tous les fichiers BIS .xlsx et renvoie un DataFrame long."""
    files = sorted(directory.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No BIS files found in {directory}")

    long_frames: List[pd.DataFrame] = []
    for file in files:
        wide = pd.read_excel(file)

        # Vérifie que les 7 premières colonnes correspondent bien aux métadonnées
        meta = wide.columns[:7]
        date_cols = wide.columns[7:]

        # Melt → long format
        long = wide.melt(
            id_vars=meta,
            value_vars=date_cols,
            var_name="date",
            value_name="value",
        )
        long_frames.append(long)

    df = pd.concat(long_frames, ignore_index=True)

    # Nettoyage : uniformise les noms de colonnes → snake_case
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Convertit la colonne date en datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df

# ------------------------------------------------------------------
# 2) FILTER UTILITIES
# ------------------------------------------------------------------

@st.cache_data
def get_filter_options(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Retourne un dict {colonne: [\"All\", ...valeurs uniques]}"""
    cols = [
        "reference_area", "frequency", "type", "basket", "unit"
    ]
    opts: Dict[str, List[str]] = {}
    for col in cols:
        values = sorted(df[col].dropna().unique().tolist())
        opts[col] = ["All"] + values
    return opts


def filter_bis_data(
    df: pd.DataFrame,
    reference_area: str = "All",
    frequency: str = "All",
    type_: str = "All",
    basket: str = "All",
    unit: str = "All",
    year: Optional[int] = None,
) -> pd.DataFrame:
    """Filtre le DataFrame BIS selon les sélections (\"All\" = pas de filtre)."""
    if reference_area != "All":
        df = df[df["reference_area"] == reference_area]
    if frequency != "All":
        df = df[df["frequency"] == frequency]
    if type_ != "All":
        df = df[df["type"] == type_]
    if basket != "All":
        df = df[df["basket"] == basket]
    if unit != "All":
        df = df[df["unit"] == unit]
    if year is not None:
        df = df[df["date"].dt.year == year]
    return df.reset_index(drop=True)

# ------------------------------------------------------------------
# TEST RAPIDE
# ------------------------------------------------------------------
if __name__ == "__main__":
    df_full = load_bis_reer_data()
    opts = get_filter_options(df_full)
    print("Columns:", df_full.columns.tolist()[:10])
    print("Sample filters:", opts)
