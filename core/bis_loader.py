# core/numbeo_loader.py – v2025‑07‑07 robust
# ---------------------------------------------------------------------
# Robust loader for Numbeo SQLite DB (cities table)
# • Gracefully handles missing/invalid DB files
# • Provides get_city_options, get_variable_options, filter_numbeo_data
# ---------------------------------------------------------------------

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = Path("data/raw/numbeo/numbeo.db")
FALLBACK_CSV = Path("data/raw/numbeo/numbeo_fallback.csv")  # optional fallback

# ------------------------------------------------------------------ #
# 1. Load data (DB → DataFrame)                                      #
# ------------------------------------------------------------------ #

@st.cache_data(show_spinner=False)
def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Load cities table from SQLite DB. If it fails, try fallback CSV."""
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
                if "cities" not in tables:
                    raise ValueError(f"Table 'cities' not found. Tables available: {tables}")
                df = pd.read_sql("SELECT * FROM cities;", conn)
                df.columns = df.columns.str.strip()
                return df
        except Exception as e:
            st.warning(f"⚠️ Failed to read SQLite DB ({e}). Trying fallback CSV…")
    # Fallback
    if FALLBACK_CSV.exists():
        st.info("Loading fallback CSV for Numbeo data…")
        return pd.read_csv(FALLBACK_CSV)
    raise FileNotFoundError("No valid Numbeo dataset available (DB or CSV fallback).")

# ------------------------------------------------------------------ #
# 2. Helpers                                                         #
# ------------------------------------------------------------------ #

def get_city_options(df: pd.DataFrame) -> list[str]:
    if "name" not in df.columns:
        raise ValueError("Column 'name' missing from Numbeo data.")
    return sorted(df["name"].dropna().astype(str).str.strip().unique())

def get_variable_options(df: pd.DataFrame) -> list[str]:
    exclude = {"id_city", "name", "status"}
    return [c for c in df.columns if c not in exclude]

# ------------------------------------------------------------------ #
# 3. Filtering                                                       #
# ------------------------------------------------------------------ #

def filter_numbeo_data(df: pd.DataFrame, regions: list[str], variables: list[str]) -> pd.DataFrame:
    """Return filtered DataFrame for selected regions and variables."""
    if "name" not in df.columns:
        raise ValueError("Column 'name' missing from Numbeo data.")
    if not regions:
        regions = df["name"].dropna().unique()  # select all
    subset = df[df["name"].isin(regions)].copy()
    cols = ["name"] + ( ["status"] if "status" in df.columns else [] ) + variables
    return subset[cols].reset_index(drop=True)
