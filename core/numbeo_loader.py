# core/numbeo_loader.py – v2025‑07‑07
# ---------------------------------------------------------------------
# ✅ Ajout d'un bouton "Select all" pour villes et variables
# ✅ Affichage des colonnes limité à 10 par défaut + bouton "Show all"
# ✅ Libellé de téléchargement mis à jour
# ---------------------------------------------------------------------

import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data

def load_numbeo_data() -> pd.DataFrame:
    path = Path("data/raw/numbeo/numbeo_cost_ppp.db")
    conn = None
    try:
        import sqlite3
        conn = sqlite3.connect(path)
        df = pd.read_sql_query("SELECT * FROM cost_of_living", conn)
    finally:
        if conn:
            conn.close()
    return df

def get_city_options(df: pd.DataFrame) -> list[str]:
    return sorted(df["name"].dropna().unique().tolist())

def get_variable_options(df: pd.DataFrame) -> list[str]:
    excluded = ["name", "status"]
    return [col for col in df.columns if col not in excluded]

def filter_numbeo_data(df: pd.DataFrame, cities: list[str], variables: list[str]) -> pd.DataFrame:
    return df[df["name"].isin(cities)][["name", "status"] + variables]

def display_numbeo_block():
    st.markdown("""### 1 – Select filters""")
    df = load_numbeo_data()

    cities = get_city_options(df)
    variables = get_variable_options(df)

    # --- Sélection des villes ---
    with st.container():
        all_cities_selected = st.checkbox("Select all cities")
        selected_cities = st.multiselect("Region (city, country)", cities, default=cities if all_cities_selected else [])

    # --- Sélection des variables ---
    with st.container():
        all_vars_selected = st.checkbox("Select all variables")
        selected_vars = st.multiselect("Variables", variables, default=variables if all_vars_selected else variables[:5])

    # --- Filtrage ---
    if selected_cities and selected_vars:
        filtered = filter_numbeo_data(df, selected_cities, selected_vars)
        st.success(f"{filtered.shape[0]} rows selected.")

        # --- Affichage des données ---
        show_all = st.checkbox("Show all columns")
        if not show_all:
            display_cols = ["name", "status"] + selected_vars[:10]
        else:
            display_cols = filtered.columns

        st.dataframe(filtered[display_cols], use_container_width=True)

        # --- Téléchargement ---
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name="numbeo_filtered.csv", mime="text/csv")
    else:
        st.warning("Please select at least one city and one variable.")
