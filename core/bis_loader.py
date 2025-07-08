# ───────────────────────── core/bis_loader.py – v2025-07-09 fixed ─────────────────────────
"""
BIS – Real Effective Exchange Rates (REER)
• Fusionne automatiquement plusieurs fichiers .csv ou .xlsx placés dans data/raw/bis_reer
• Conserve une seule ligne par « Timeseries Key » (méta) et ajoute seulement les nouvelles dates
• Fournit les options de filtre + fonction de filtrage
"""

from pathlib import Path
import pandas as pd
import re

# Chemin vers les fichiers BIS-REER
DATA_DIR = Path("data/raw/bis_reer")

# Colonnes méta (jamais considérées comme dates)
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
# 1. Nettoyage des noms de colonnes
# ─────────────────────────────────────────────────────────────
def _clean_columns(cols: list[str]) -> list[str]:
    """Normalise les noms de colonnes (espaces, alias, casse)."""
    normalized = []
    for c in cols:
        c = re.sub(r"\s+", " ", c.replace("\u00A0", " ")).strip()
        low = c.lower()
        if low in {"reference area", "reference-area"}:
            c = "Reference area"
        elif low in {"dataflowid", "dataflow id"}:
            c = "Dataflow ID"
        elif low in {"timeseries key", "timeserieskey"}:
            c = "Timeseries Key"
        normalized.append(c)
    return normalized

# ─────────────────────────────────────────────────────────────
# 2. Chargement + fusion intelligente
# ─────────────────────────────────────────────────────────────
def load_bis_reer_data() -> pd.DataFrame:
    """
    Charge et fusionne tous les fichiers BIS-REER (.csv et .xlsx) présents dans DATA_DIR.
    • Une seule ligne par « Timeseries Key »
    • Les nouvelles dates sont ajoutées sans dupliquer les colonnes méta
    Renvoie un DataFrame vide (colonnes méta uniquement) si aucun fichier n’est trouvé.
    """
    # Repère les deux extensions possibles
    files = list(DATA_DIR.glob("*.csv")) + list(DATA_DIR.glob("*.xlsx"))
    files = sorted(files)

    if not files:
        print("⚠️ Aucun fichier BIS-REER trouvé dans", DATA_DIR)
        return pd.DataFrame(columns=META_COLS)

    merged: dict[str, pd.Series] = {}

    for path in files:
        try:
            df = pd.read_csv(path) if path.suffix == ".csv" else pd.read_excel(path)
        except Exception as err:
            print(f"❌ Erreur lecture {path.name} : {err}")
            continue

        df.columns = _clean_columns(df.columns.tolist())

        # Sépare méta et dates
        date_cols = [c for c in df.columns if c not in META_COLS]

        for _, row in df.iterrows():
            key = row["Timeseries Key"]
            meta_part  = row[META_COLS]
            date_part  = row[date_cols]

            if key not in merged:
                # Première fois qu’on voit cette clé → on stocke méta + dates
                merged[key] = pd.concat([meta_part, date_part])
            else:
                # Contrôle de cohérence méta (facultatif mais utile en debug)
                if not merged[key][META_COLS].equals(meta_part):
                    print(f"⚠️ Conflit méta sur Timeseries Key « {key} » entre fichiers ; "
                          "on garde les premières valeurs rencontrées.")
                # Ajoute uniquement les dates manquantes
                existing_dates = [idx for idx in merged[key].index if idx not in META_COLS]
                new_dates = [d for d in date_part.index if d not in existing_dates]
                if new_dates:
                    merged[key] = pd.concat([merged[key], date_part[new_dates]])

    # Dictionnaire → DataFrame
    merged_df = pd.DataFrame(merged).T.reset_index(drop=True)

    # Ré-ordonne : méta d’abord, dates ensuite
    meta_existing = [c for c in META_COLS if c in merged_df.columns]
    date_existing = sorted([c for c in merged_df.columns if c not in meta_existing])

    return merged_df[meta_existing + date_existing]

# ─────────────────────────────────────────────────────────────
# 3. Options de filtre pour l’interface
# ─────────────────────────────────────────────────────────────
def get_filter_options(df: pd.DataFrame) -> dict[str, list]:
    """Retourne un dict {colonne: liste triée des valeurs uniques}."""
    return {
        col: sorted(df[col].dropna().unique().tolist()) if col in df.columns else []
        for col in ["Frequency", "Type", "Basket", "Unit", "Reference area"]
    }

# ─────────────────────────────────────────────────────────────
# 4. Filtrage selon les sélections utilisateur
# ─────────────────────────────────────────────────────────────
def filter_bis_data(df: pd.DataFrame, selections: dict) -> pd.DataFrame:
    """
    Applique un filtre {colonne: [valeurs]}.
    • Si la liste est vide → aucune restriction sur cette colonne.
    """
    out = df.copy()
    for col, vals in selections.items():
        if vals and col in out.columns:
            out = out[out[col].isin(vals)]
    return out.reset_index(drop=True)
