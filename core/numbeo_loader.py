# core/numbeo_loader.py
# ---------------------------------------------------------------------
# Utilities for loading and filtering data from the Numbeo SQLite DB
# Adapted to the current structure of the **cities** table
# ---------------------------------------------------------------------

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# 📍 Path to the Numbeo SQLite file
DB_PATH = Path("data/raw/numbeo/numbeo.db")

# ------------------------------------------------------------------ #
# 1. Load full table                                                  #
# ------------------------------------------------------------------ #

def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Load the **cities** table from Numbeo DB into a DataFrame."""
    if not db_path.exists():
        raise FileNotFoundError(f"Numbeo DB not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        # Ensure the 'cities' table exists
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
        if "cities" not in tables:
            raise ValueError(f"Table 'cities' not found in {db_path}. Tables available: {tables}")

        df = pd.read_sql("SELECT * FROM cities;", conn)

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df

# ------------------------------------------------------------------ #
# 2. Helper – city selector                                           #
# ------------------------------------------------------------------ #

@st.cache_data(show_spinner=False)
def get_city_options(df: pd.DataFrame) -> list[str]:
    """Return sorted unique city names for dropdown."""
    for col in ["city", "name", "city_name", "location"]:
        if col in df.columns:
            return sorted(df[col].dropna().unique())
    raise ValueError(
        "No city-like column found in Numbeo dataset. Columns present: "
        f"{df.columns.tolist()}"
    )

# ------------------------------------------------------------------ #
# 3. Helper – variable selector                                       #
# ------------------------------------------------------------------ #

def get_variable_options(df: pd.DataFrame) -> list[str]:
    """Return numeric/cost variables excluding identifiers."""
    id_cols = {"id_city", "name", "city", "city_name", "location", "status"}
    return [c for c in df.columns if c not in id_cols]

# ------------------------------------------------------------------ #
# 4. Filter function                                                  #
# ------------------------------------------------------------------ #

def filter_numbeo_data(
    df: pd.DataFrame,
    city: str,
    variables: list[str] | None = None,
) -> pd.DataFrame:
    """Return rows for a given city and subset of variables."""
    # Detect the city column again (robust)
    city_col = next((c for c in ["city", "name", "city_name", "location"] if c in df.columns), None)
    if city_col is None:
        raise ValueError("No city column detected after loading Numbeo data.")

    subset = df[df[city_col] == city].copy()

    if variables:  # keep only requested variables + identifier columns
        keep_cols = [city_col, "status"] + variables if "status" in df.columns else [city_col] + variables
        subset = subset[keep_cols]

    return subset.reset_index(drop=True)
