# core/penn_loader.py
# ---------------------------------------------------------------------
# Loader & filter utilities for Penn World Table (PWT 10.01 or similar)
# ---------------------------------------------------------------------
# Expected file location (default):
#   data/raw/penn_world_table/Penn World Table.xlsx
# If you rename / relocate the file, pass the new path to load_penn_data().

from pathlib import Path
from functools import lru_cache
import pandas as pd
import streamlit as st

DEFAULT_PATH = Path("data/raw/penn_world_table/Penn World Table.xlsx")

# ------------------------------------------------------------------
# 1) LOAD DATA ------------------------------------------------------
# ------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_penn_data(path: Path | str = DEFAULT_PATH) -> pd.DataFrame:
    """Loads the Penn World Table Excel file into a DataFrame."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Penn World Table file not found → {file_path}")

    df = pd.read_excel(file_path)

    # Standardise column names (strip, lower, replace spaces with _)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

# ------------------------------------------------------------------
# 2) OPTIONS HELPERS ------------------------------------------------
# ------------------------------------------------------------------

@st.cache_data
def get_country_options(df: pd.DataFrame) -> list[str]:
    """Returns a sorted list of country names."""
    return sorted(df["country"].dropna().unique())


@st.cache_data
def get_variable_options(df: pd.DataFrame) -> list[str]:
    """Returns numeric variable columns (excluding id columns)."""
    exclude = {"countrycode", "country", "currency_unit", "year"}
    numeric_cols = [
        c for c in df.columns
        if c not in exclude and pd.api.types.is_numeric_dtype(df[c])
    ]
    return numeric_cols

# ------------------------------------------------------------------
# 3) FILTER FUNCTION ------------------------------------------------
# ------------------------------------------------------------------

def filter_penn_data(
    df: pd.DataFrame,
    country: str,
    variables: list[str] | None = None,
    years: list[int] | None = None,
) -> pd.DataFrame:
    """Filter the Penn data by country, variables, and years.

    Args:
        df (pd.DataFrame): full dataset
        country (str): country name selected
        variables (list[str] | None): variables to keep (None = all)
        years (list[int] | None): list of years; None = all years
    """
    # Filter by country
    df = df[df["country"] == country]

    # Filter by years if provided
    if years is not None:
        df = df[df["year"].isin(years)]

    # Keep id columns + selected variables
    id_cols = ["countrycode", "country", "currency_unit", "year"]
    if variables:
        keep_cols = id_cols + variables
    else:
        keep_cols = id_cols + get_variable_options(df)

    return df[keep_cols].reset_index(drop=True)

# ------------------------------------------------------------------
# Quick test --------------------------------------------------------
# ------------------------------------------------------------------
if __name__ == "__main__":
    data = load_penn_data()
    print("Columns:", data.columns.tolist()[:10])
    print("Countries →", get_country_options(data)[:5])
    print("Variables →", get_variable_options(data)[:5])
