# core/bis_loader.py – v2025-07-09 clean_cols
# ------------------------------------------------------------
# BIS – Real Effective Exchange Rates (REER)
# • Fusionne les CSV présents dans data/raw/bis_reer
# • Nettoie / standardise les noms de colonnes
# • Fournit options de filtre + fonction de filtrage
# ------------------------------------------------------------

from pathlib import Path
import pandas as pd
import re

# Dossier contenant les fichiers CSV REER
DATA_DIR = Path("data/raw/bis_reer")

# Colonnes “méta” (ne doivent pas être traitées comme dates)
META_COLS = [
    "Dataflow ID",
    "Timeseries Key",
    "Frequency",
    "Type",
    "Basket",
    "Reference area",
    "Unit",
]

# ─────────────────────────────────────────────────────────────
# 1. Outil de nettoyage de colonnes
# ─────────────────────────────────────────────────────────────
def _clean_columns(cols: list[str]) -> list[str]:
    """Normalise les noms de colonnes (strip, espaces multiples, casse)."""
    std = []
    for c in cols:
        # Supprime espaces insécables + multiples
        c = re.sub(r"\s+", " ", c.replace("\u00A0", " ")).strip()
        # Harmonise quelques alias
        if c.lower() in {"reference area", "reference-area"}:
            c = "Reference area"
        elif c.lower() in {"dataflowid", "dataflow id"}:
            c = "Dataflow ID"
        elif c.lower() in {"timeseries key", "timeserieskey"}:
            c = "Timeseries Key"
        std.append(c)
    return std

# ─────────────────────────────────────────────────────────────
# 2. Chargement + fusion intelligente
# ─────────────────────────────────────────────────────────────
def load_bis_reer_data() -> pd.DataFrame:
    """Charge et fusionne tous les fichiers CSV BIS-REER présents dans DATA_DIR."""
    files = sorted(DATA_DIR.glob("*.csv"))
    if not files:
        # DataFrame vide conforme
        return pd.DataFrame(columns=META_COLS)

    merged: dict[str, pd.Series] = {}

    for csv_path in files:
        try:
            df = pd.read_csv(csv_path)
        except Exception as err:
            print(f"❌ Erreur lecture {csv_path.name} : {err}")
            continue

        # Nettoie / normalise les noms de colonnes
        df.columns = _clean_columns(df.columns.tolist())

        # Sépare méta & dates dynamiquement
        date_cols = [c for c in df.columns if c not in META_COLS]

        for _, row in df.iterrows():
            key = row["Timeseries Key"]
            meta_part = row[META_COLS]
            date_part = row[date_cols]

            if key not in merged:
                merged[key] = pd.concat([meta_part, date_part])
            else:
                # Ajoute uniquement les nouvelles dates
                existing_dates = merged[key].index.difference(META_COLS)
                new_dates = [d for d in date_part.index if d not in existing_dates]
                merged[key] = pd.concat([merged[key], date_part[new_dates]])

    merged_df = pd.DataFrame(merged).T.reset_index(drop=True)

    # Ré-ordre colonnes : méta puis dates triées
    meta_existing = [c for c in META_COLS if c in merged_df.columns]
    date_existing = sorted([c for c in merged_df.columns if c not in meta_existing])
    return merged_df[meta_existing + date_existing]

# ─────────────────────────────────────────────────────────────
# 3. Extraction des options de filtre
# ─────────────────────────────────────────────────────────────
def get_filter_options(df: pd.DataFrame) -> dict:
    """Retourne {colonne : liste triée des valeurs uniques}. Toujours non-nul si la colonne existe."""
    return {
        col: sorted(df[col].dropna().unique().tolist()) if col in df.columns else []
        for col in ["Frequency", "Type", "Basket", "Unit", "Reference area"]
    }

# ─────────────────────────────────────────────────────────────
# 4. Filtrage selon les sélections utilisateur
# ─────────────────────────────────────────────────────────────
def filter_bis_data(df: pd.DataFrame, selections: dict) -> pd.DataFrame:
    """
    Filtre le DataFrame selon un dict {colonne: [valeurs retenues]}.
    Si liste vide → on garde tout.
    """
    out = df.copy()
    for col, vals in selections.items():
        if vals and col in out.columns:
            out = out[out[col].isin(vals)]
    return out.reset_index(drop=True)
