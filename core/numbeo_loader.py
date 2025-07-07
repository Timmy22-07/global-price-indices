# core/numbeo_loader.py – v2025-07-08
# ------------------------------------------------------------
# • Chemins robustes (relatifs au fichier courant)            |
# • Lecture DB ➜ fallback CSV ➜ FileNotFoundError             |
# • Helpers: get_city_options / get_variable_options          |
# • Filtrage conservant name [+ status] + variables choisies  |
# ------------------------------------------------------------
from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# ── Chemins absolus basés sur ce fichier ─────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent        #  …/core/..
DATA_DIR = ROOT_DIR / "data" / "raw" / "numbeo"

DB_PATH       = DATA_DIR / "numbeo"
FALLBACK_CSV  = DATA_DIR / "numbeo_fallback.csv"         # optionnel

# ── Chargement (DB puis évent. CSV) ──────────────────────────
@st.cache_data(show_spinner=False)
def load_numbeo_data() -> pd.DataFrame:
    """Charge les données Numbeo à partir d’un .db (SQLite) ou d’un CSV de secours."""
    if DB_PATH.exists():
        try:
            with sqlite3.connect(DB_PATH) as conn:
                first_table = pd.read_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;",
                    conn,
                )["name"].iat[0]
                df = pd.read_sql(f"SELECT * FROM {first_table};", conn)
                df.columns = df.columns.str.strip()
                return df
        except Exception as err:
            st.warning(f"⚠️ Lecture de la base Numbeo impossible : {err}")

    if FALLBACK_CSV.exists():
        st.info("⏪  Basculage sur le CSV de secours Numbeo…")
        return pd.read_csv(FALLBACK_CSV)

    raise FileNotFoundError(
        "Aucune source valide pour les données Numbeo : "
        f"{DB_PATH} ni {FALLBACK_CSV} n’existent."
    )

# ── Helpers pour les listes déroulantes ──────────────────────
def get_city_options(df: pd.DataFrame) -> list[str]:
    if "name" not in df.columns:
        raise ValueError("Colonne 'name' introuvable dans Numbeo.")
    return sorted(df["name"].dropna().astype(str).str.strip().unique())

def get_variable_options(df: pd.DataFrame) -> list[str]:
    exclude = {"id_city", "name", "status"}
    return [c for c in df.columns if c not in exclude]

# ── Filtrage principal ───────────────────────────────────────
def filter_numbeo_data(
    df: pd.DataFrame,
    regions: list[str] | None,
    variables: list[str],
) -> pd.DataFrame:
    """Filtre par régions et variables sélectionnées."""
    if "name" not in df.columns:
        raise ValueError("Colonne 'name' introuvable.")
    if not regions:
        regions = df["name"].dropna().unique()

    subset = df[df["name"].isin(regions)].copy()
    cols   = ["name"] + (["status"] if "status" in subset.columns else []) + variables
    return subset[cols].reset_index(drop=True)
