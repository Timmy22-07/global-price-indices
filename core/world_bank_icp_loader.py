# core/world_bank_icp_loader.py
# ---------------------------------------------------------------
# Loader and filter functions for World Bank – ICP Excel dataset
# ---------------------------------------------------------------

import pandas as pd
from pathlib import Path
import streamlit as st

# Path to the World Bank ICP Excel file
ICP_PATH = Path("data/raw/world_bank/World Bank ICP.xlsx")

# Load the dataset
@st.cache_data
def load_icp_data():
    df = pd.read_excel(ICP_PATH, skiprows=0)
    df.columns = df.columns.str.strip()
    # Clean year columns (e.g., '2011 [YR2011]' → 2011)
    df.rename(columns={c: int(c[:4]) for c in df.columns if c[:4].isdigit()}, inplace=True)
    return df

# Get unique country names
@st.cache_data
def get_country_options(df):
    return sorted(df["Country Name"].dropna().unique())

# Get metadata options
@st.cache_data
def get_metadata_options(df):
    classification_names = df["Classification Name"].dropna().unique()
    series_names = df["Series Name"].dropna().unique()
    return sorted(classification_names), sorted(series_names)

# Get all available years (based on column names)
@st.cache_data
def get_year_options(df):
    return sorted([col for col in df.columns if isinstance(col, int)])

# Filter the data based on selected values (All → None)
def filter_icp_data(df, country=None, classification_name=None, series_name=None, year=None):
    filtered = df.copy()

    if country:
        filtered = filtered[filtered["Country Name"] == country]
    if classification_name:
        filtered = filtered[filtered["Classification Name"] == classification_name]
    if series_name:
        filtered = filtered[filtered["Series Name"] == series_name]

    # Selection des colonnes finales (année ou tout)
    base_cols = [
        "Country Name", "Country Code", 
        "Classification Name", "Classification Code",
        "Series Name", "Series Code"
    ]
    if year:
        year_cols = [year] if isinstance(year, int) else year
        filtered = filtered[base_cols + year_cols]
    else:
        filtered = filtered.dropna(axis=1, how="all")  # supprime colonnes vides

    return filtered.reset_index(drop=True)
