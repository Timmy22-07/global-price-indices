# core/numbeo_loader.py
# ---------------------------------------------------------------------
# Utilities for loading and filtering data from the Numbeo SQLite DB
# ---------------------------------------------------------------------

import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st

DB_PATH = Path("data/raw/numbeo/numbeo.db")  # ← adapte ce chemin si besoin

def load_numbeo_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """
    Load the full Numbeo data from a SQLite .db file into a DataFrame.
    Assumes a table named 'cost_of_living' is present.

    Returns:
        pd.DataFrame: Complete dataset
    """
    conn = sqlite3.connect(db_path)
    # auto-detect first table (assumed to be 'cost_of_living')
    table_name = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;", conn
    ).iloc[0, 0]

    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    conn.close()
    return df


@st.cache_data
def get_city_options(df: pd.DataFrame) -> list:
    """
    Extracts unique cities for filtering dropdown.

    Args:
        df (pd.DataFrame): Loaded Numbeo data

    Returns:
        list: Sorted list of cities
    """
    if "city" not in df.columns:
        raise ValueError("No 'city' column found in Numbeo database.")
    return sorted(df["city"].dropna().unique())


def filter_numbeo_data(df: pd.DataFrame, city: str) -> pd.DataFrame:
    """
    Filter Numbeo data by selected city.

    Args:
        df (pd.DataFrame): Full Numbeo dataset
        city (str): Selected city

    Returns:
        pd.DataFrame: Filtered data
    """
    return df[df["city"] == city].copy()

