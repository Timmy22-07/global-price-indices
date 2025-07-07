# core/world_bank_cpi_loader.py
# ---------------------------------------------------------------------
# Loader & utilities for World Bank CPI data split into decade files
# ---------------------------------------------------------------------
# Expected folder structure:
#   data/raw/world_bank/
#       World Bank CPI (1960-1965).xlsx
#       World Bank CPI (1966-1971).xlsx
#       ...
# All files share identical columns:
#   - Country Name, Country Code, Series Name, Series Code
#   - followed by yearly columns like "1960 [YR1960]", "1961 [YR1961]", ...

import re
from pathlib import Path
from typing import List, Optional
import pandas as pd
import streamlit as st

WB_DIR = Path("data/raw/world_bank")
PATTERN = "World Bank CPI ("  # to match only CPI files

# ------------------------------------------------------------------
# 1) LOAD & TRANSFORM ------------------------------------------------
# ------------------------------------------------------------------

def _clean_year_col(col: str) -> Optional[int]:
    """Extracts the year as int from a column '1960 [YR1960]'. Returns None if not a year."""
    m = re.match(r"(\d{4})", str(col))
    if m:
        return int(m.group(1))
    return None


def load_wb_cpi_data(directory: Path = WB_DIR) -> pd.DataFrame:
    """Load all CPI Excel files, reshape to long format, and concatenate."""
    files = sorted([f for f in directory.glob("*.xlsx") if PATTERN in f.name])
    if not files:
        raise FileNotFoundError("No World Bank CPI files found in data/raw/world_bank/")

    long_frames: List[pd.DataFrame] = []
    for f in files:
        wide = pd.read_excel(f)
        meta_cols = ["Country Name", "Country Code", "Series Name", "Series Code"]
        year_cols = [c for c in wide.columns if _clean_year_col(c)]

        # Melt to long
        long = wide.melt(id_vars=meta_cols, value_vars=year_cols, var_name="year_raw", value_name="value")
        long["year"] = long["year_raw"].apply(_clean_year_col)
        long = long.drop(columns=["year_raw"]).dropna(subset=["year"])
        long_frames.append(long)

    df = pd.concat(long_frames, ignore_index=True)
    # Rename meta columns to snake_case for consistency
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

# ------------------------------------------------------------------
# 2) OPTIONS ---------------------------------------------------------
# ------------------------------------------------------------------

@st.cache_data
def get_country_options(df: pd.DataFrame) -> List[str]:
    return sorted(df["country_name"].unique())


@st.cache_data
def get_series_options(df: pd.DataFrame) -> List[str]:
    return sorted(df["series_name"].unique())


@st.cache_data
def get_year_options(df: pd.DataFrame) -> List[int]:
    return sorted(df["year"].unique())

# ------------------------------------------------------------------
# 3) FILTER ----------------------------------------------------------
# ------------------------------------------------------------------

def filter_wb_cpi_data(
    df: pd.DataFrame,
    country: str,
    series: str,
    years: Optional[List[int]] = None,
) -> pd.DataFrame:
    sub = df[(df["country_name"] == country) & (df["series_name"] == series)]
    if years is not None:
        sub = sub[sub["year"].isin(years)]
    return sub.reset_index(drop=True)

# ------------------------------------------------------------------
# Quick test ---------------------------------------------------------
# ------------------------------------------------------------------
if __name__ == "__main__":
    data = load_wb_cpi_data()
    print("Countries:", get_country_options(data)[:5])
    print("Series:", get_series_options(data)[:5])
    print("Years range:", min(get_year_options(data)), "-", max(get_year_options(data)))
