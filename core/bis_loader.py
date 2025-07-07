# core/bis_loader.py – v2025-07-08 merge_by_timeseries_key
# ---------------------------------------------------------------------
# BIS – Real Effective Exchange Rates (REER)
# • Fusionne plusieurs CSV sans dupliquer les colonnes de métadonnées
# • Options dynamiques : Frequency, Type, Basket, Unit, Reference area
# • Filtrage basé sur les choix utilisateur
# ---------------------------------------------------------------------

from pathlib import Path
import pandas as pd

# Dossier contenant les fichiers CSV REER
DATA_DIR = Path("data/raw/bis_reer")

# Colonnes de métadonnées (ne doivent pas être répétées)
META_COLS = [
    "Dataflow ID",
    "Timeseries Key",
    "Frequency",
    "Type",
    "Basket",
    "Reference area",
    "Unit",
]

# ------------------------------------------------------------------ #
# 1. Chargement + fusion intelligente                                #
# ------------------------------------------------------------------ #
def load_bis_reer_data() -> pd.DataFrame:
    """
    Charge et fusionne tous les fichiers CSV BIS-REER.

    • Une seule ligne par « Timeseries Key »
    • Les colonnes de dates sont agrégées (aucun écrasement)
    """
    files = list(DATA_DIR.glob("*.csv"))
    if not files:
        return pd.DataFrame(columns=META_COLS)  # évite les crashs

    # Dictionnaire { timeseries_key : Series (meta + dates) }
    merged: dict[str, pd.Series] = {}

    for csv_path in files:
        try:
            df = pd.read_csv(csv_path)
        except Exception as err:
            print(f"❌ Erreur lecture {csv_path.name} : {err}")
            continue

        # Séparation méta + dates
        date_cols = [c for c in df.columns if c not in META_COLS]
        for _, row in df.iterrows():
            key = row["Timeseries Key"]

            # Séries méta (une seule fois) + valeurs dates
            meta_part = row[META_COLS]
            date_part = row[date_cols]

            if key not in merged:
                merged[key] = pd.concat([meta_part, date_part])
            else:
                # Ajoute seulement les nouvelles dates
                merged[key] = pd.concat([merged[key], date_part], axis=0)

    # Repassage en DataFrame
    merged_df = pd.DataFrame(merged).T.reset_index(drop=True)

    # Ré-ordonne : méta d’abord puis dates (triées chronologiquement)
    meta_existing = [c for c in META_COLS if c in merged_df.columns]
    date_existing = sorted([c for c in merged_df.columns if c not in meta_existing])
    merged_df = merged_df[meta_existing + date_existing]

    return merged_df

# ------------------------------------------------------------------ #
# 2. Extraction des options de filtre                                #
# ------------------------------------------------------------------ #
def get_filter_options(df: pd.DataFrame) -> dict:
    """Retourne un dictionnaire des options possibles pour chaque filtre."""
    return {
        "Frequency": sorted(df["Frequency"].dropna().unique()) if "Frequency" in df.columns else [],
        "Type":       sorted(df["Type"].dropna().unique())       if "Type"       in df.columns else [],
        "Basket":     sorted(df["Basket"].dropna().unique())     if "Basket"     in df.columns else [],
        "Unit":       sorted(df["Unit"].dropna().unique())       if "Unit"       in df.columns else [],
        "Reference area": sorted(df["Reference area"].dropna().unique()) if "Reference area" in df.columns else [],
        # Les colonnes de dates sont laissées à la sélection libre dans le bloc UI
    }

# ------------------------------------------------------------------ #
# 3. Filtrage selon les paramètres sélectionnés                      #
# ------------------------------------------------------------------ #
def filter_bis_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Filtre les données selon un dict :
      { "Frequency": [...], "Type": [...], ... }
    """
    out = df.copy()
    for col, values in filters.items():
        if values and col in out.columns:
            out = out[out[col].isin(values)]
    return out.reset_index(drop=True)
