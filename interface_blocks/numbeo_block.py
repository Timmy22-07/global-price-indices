# interface_blocks/numbeo_block.py – v2025‑07‑07 final
# ---------------------------------------------------------------------
# ✅ Ajout d'un bouton "Select all" pour villes et variables
# ✅ Affichage limité à 10 colonnes + "Show all columns"
# ✅ Libellé du bouton de téléchargement → "Download CSV"
# ---------------------------------------------------------------------

import streamlit as st
import pandas as pd
from pathlib import Path
from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    get_variable_options,
    filter_numbeo_data,
)

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

        # --- Affichage limité à 10 colonnes ---
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
