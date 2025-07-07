# core/numbeo_loader.py – v2025-07-08 final
# ------------------------------------------------------------
# Chargement intelligent d’un fichier Numbeo (.db ou CSV)
# Détection automatique d’un fichier SQLite même sans extension
# Helpers : get_city_options, get_variable_options, filter_numbeo_data
# ------------------------------------------------------------

from __future__ import annotations
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# ── Chemin vers le dossier contenant les données ─────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "numbeo"
FALLBACK_CSV = DATA_DIR / "numbeo_fallback.csv"

# ── Détection automatique d’un fichier SQLite ────────────────
def _find_numbeo_file() -> Path | None:
    for f in DATA_DIR.iterdir():
        if f.is_file() and f.suffix in {"", ".db"}:
            try:
                with f.open("rb") as fh:
                    if fh.read(16) == b"SQLite format 3\x00":
                        return f
            except Exception:
                continue
    return None

# ── Chargement principal des données ─────────────────────────
@st.cache_data(show_spinner=False)
def load_numbeo_data() -> pd.DataFrame:
    db_file = _find_numbeo_file()

    if db_file:
        try:
            with sqlite3.connect(db_file) as conn:
                table_name = pd.read_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;", conn
                )["name"].iat[0]
                df = pd.read_sql(f"SELECT * FROM {table_name};", conn)
                df.columns = df.columns.str.strip()
                return df
        except Exception as e:
            st.warning(f"⚠️ Lecture impossible de {db_file.name} : {e}")

    if FALLBACK_CSV.exists():
        st.info("⏪ Chargement du fichier CSV de secours Numbeo…")
        return pd.read_csv(FALLBACK_CSV)

    raise FileNotFoundError("❌ Aucun fichier Numbeo valide trouvé (.db ou CSV).")

# ── Liste des villes/régions ────────────────────────────────
def get_city_options(df: pd.DataFrame) -> list[str]:
    if "name" not in df.columns:
        raise ValueError("Colonne 'name' introuvable.")
    return sorted(df["name"].dropna().astype(str).str.strip().unique())

# ── Liste des variables affichables ──────────────────────────
def get_variable_options(df: pd.DataFrame) -> list[str]:
    exclude = {"id_city", "name", "status"}
    return [col for col in df.columns if col not in exclude]

# ── Filtrage de l’affichage ─────────────────────────────────
def filter_numbeo_data(
    df: pd.DataFrame,
    regions: list[str] | None,
    variables: list[str],
) -> pd.DataFrame:
    if "name" not in df.columns:
        raise ValueError("Colonne 'name' introuvable.")
    if not regions:
        regions = df["name"].dropna().unique()

    filtered = df[df["name"].isin(regions)].copy()
    cols = ["name"] + (["status"] if "status" in df.columns else []) + variables
    return filtered[cols].reset_index(drop=True)
