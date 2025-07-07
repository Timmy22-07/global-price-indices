# core/numbeo_loader.py – v2
# ---------------------------------------------------------------------
# Utilities for loading and filtering data from the Numbeo SQLite DB
# Adapted to the current structure of the **cities** table
# ---------------------------------------------------------------------

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = Path("data/raw/numbeo/numbeo.db")

def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    if not db_path.exists():
        raise FileNotFoundError(f"Numbeo DB not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
        if "cities" not in tables:
            raise ValueError(f"Table 'cities' not found in {db_path}. Tables available: {tables}")

        df = pd.read_sql("SELECT * FROM cities;", conn)

    df.columns = df.columns.str.strip()
    return df

@st.cache_data(show_spinner=False)
def get_variable_options(df: pd.DataFrame) -> list[str]:
    id_cols = {"id_city", "name", "city", "city_name", "location", "status"}
    return [c for c in df.columns if c not in id_cols]

def filter_numbeo_data(df: pd.DataFrame, region: str, variables: list[str] | None = None) -> pd.DataFrame:
    if "name" not in df.columns:
        raise ValueError("Column 'name' not found in Numbeo dataset.")

    subset = df[df["name"] == region].copy()

    if variables:
        keep_cols = ["name", "status"] + variables if "status" in df.columns else ["name"] + variables
        subset = subset[keep_cols]

    return subset.reset_index(drop=True)
