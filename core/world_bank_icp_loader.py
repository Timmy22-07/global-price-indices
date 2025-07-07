# core/world_bank_icp_loader.py – v2025-07-08
# ---------------------------------------------------------------
# Loader and filter functions for World Bank – ICP Excel dataset
# ---------------------------------------------------------------

import pandas as pd
from pathlib import Path
import streamlit as st
import re

# Path to the World Bank ICP Excel file
ICP_PATH = Path("data/raw/world_bank/World Bank ICP.xlsx")

# Utility: convert column names to snake_case
def to_snake_case(s):
    s = re.sub(r"[^\w\s]", "", s)  # Remove special characters
    s = re.sub(r"\s+", "_", s)     # Replace whitespace with underscores
    return s.lower().strip()

# Load the dataset
@st.cache_data
def load_icp_data():
    df = pd.read_excel(ICP_PATH, skiprows=0)
    df.columns = df.columns.str.strip()

    # Convert all columns to snake_case
    df.columns = [to_snake_case(col) if not isinstance(col, int) else col for col in df.columns]

    # Rename year columns (e.g. '2011 [YR2011]' → 2011)
    df.rename(columns={c: int(c[:4]) for c in df.columns if isinstance(c, str) and c[:4].isdigit()}, inplace=True)
    return df

# Get unique country names
@st.cache_data
def get_country_options(df):
    return sorted(df["country_name"].dropna().unique())

# Get metadata options
@st.cache_data
def get_metadata_options(df):
    classification_names = df["classification_name"].dropna().unique()
    series_names = df["series_name"].dropna().unique()
    return sorted(classification_names), sorted(series_names)

# Get all available years (based on column names)
@st.cache_data
def get_year_options(df):
    return sorted([col for col in df.columns if isinstance(col, int)])

# Filter the data based on selected values (All → None)
def filter_icp_data(df, country=None, classification_name=None, series_name=None, years=None):
    filtered = df.copy()

    if country:
        filtered = filtered[filtered["country_name"] == country]
    if classification_name:
        filtered = filtered[filtered["classification_name"] == classification_name]
    if series_name:
        filtered = filtered[filtered["series_name"] == series_name]

    # Select relevant columns
    base_cols = [
        "country_name", "country_code", 
        "classification_name", "classification_code",
        "series_name", "series_code"
    ]

    if years:
        year_cols = [years] if isinstance(years, int) else years
        filtered = filtered[base_cols + year_cols]
    else:
        filtered = filtered.dropna(axis=1, how="all")

    return filtered.reset_index(drop=True)
